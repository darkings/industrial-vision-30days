# -- coding: utf-8 --
"""
Day 8：海康工业相机曝光时间对比实验。

本节目标：

1. 固定同一台相机和同一场景，只改变 ExposureTime。
2. 分别抓取多张图像，保存到 outputs/exposure_comparison。
3. 统计每张图的灰度均值、最小值、最大值、过曝像素数量和过曝比例。
4. 用数据观察曝光时间对图像亮度和过曝的影响。

注意：

当前没有稳定支架和稳定光源，所以本实验只学习参数影响，
不用于尺寸测量、缺陷检测或稳定 OK/NG 判断。
"""

import sys
import time
from ctypes import POINTER, byref, cast, memset, sizeof
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "exposure_comparison"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from test01_hik_sdk_grab_one_frame import (
    check_sdk_ret,
    convert_frame_to_numpy,
    load_hik_sdk,
    print_device_list,
)

# 本次实验的曝光时间，单位是微秒 us。
# 1000 us = 1 ms，3000 us = 3 ms，5000 us = 5 ms。
#
# 这里故意先倒序、再正序跑一遍，用来判断：
# - 亮度变化是否真的跟 ExposureTime 相关；
# - 还是受取流缓存、参数生效延迟、场景移动等因素影响。
EXPOSURE_TIMES_US = [800.0, 1000.0, 1500.0]
# 改曝光后等待和丢帧，是为了让后续统计更接近新参数下的稳定帧。
SETTLE_SECONDS = 0.2
DISCARD_FRAMES_AFTER_CHANGE = 5


def calculate_image_stats(image):
    """
    统计一张灰度或彩色图像的基础亮度信息。

    返回字段：

    - width：图像宽度
    - height：图像高度
    - mean_gray：平均灰度
    - min_gray：最暗像素
    - max_gray：最亮像素
    - overexposed_pixels：灰度等于 255 的像素数量
    - overexposed_ratio：过曝像素比例，单位 %
    """

    import numpy as np

    if image.ndim == 3:
        import cv2

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    height, width = gray.shape[:2]
    pixel_count = width * height
    overexposed_pixels = int(np.count_nonzero(gray == 255))

    return {
        "width": width,
        "height": height,
        "mean_gray": round(float(np.mean(gray)), 2),
        "min_gray": int(np.min(gray)),
        "max_gray": int(np.max(gray)),
        "overexposed_pixels": overexposed_pixels,
        "overexposed_ratio": round(overexposed_pixels / pixel_count * 100, 2),
    }


def set_manual_exposure(cam, exposure_time_us: float) -> None:
    """
    关闭自动曝光，并设置手动曝光时间。

    ExposureAuto = 0 表示关闭自动曝光。
    ExposureTime 的单位通常是微秒 us。
    """

    ret = cam.MV_CC_SetEnumValue("ExposureAuto", 0)
    check_sdk_ret(ret, "关闭自动曝光")

    ret = cam.MV_CC_SetFloatValue("ExposureTime", float(exposure_time_us))
    check_sdk_ret(ret, f"设置曝光时间 {exposure_time_us} us")


def get_current_exposure_time(sdk, cam) -> float:
    """
    从相机读回当前 ExposureTime。

    工业相机调参时，推荐养成这个习惯：
    Set 之后马上 Get 一次，确认参数真的被相机接受。
    """

    exposure_value = sdk.MVCC_FLOATVALUE()
    memset(byref(exposure_value), 0, sizeof(exposure_value))

    ret = cam.MV_CC_GetFloatValue("ExposureTime", exposure_value)
    check_sdk_ret(ret, "读取当前曝光时间")

    return float(exposure_value.fCurValue)


def grab_one_frame_from_open_camera(sdk, cam):
    """
    从已经打开并开始取流的相机中抓取一帧图像。
    """

    frame_out = sdk.MV_FRAME_OUT()
    memset(byref(frame_out), 0, sizeof(frame_out))

    ret = cam.MV_CC_GetImageBuffer(frame_out, 1000)
    check_sdk_ret(ret, "抓取一帧")

    try:
        return convert_frame_to_numpy(sdk, cam, frame_out)
    finally:
        cam.MV_CC_FreeImageBuffer(frame_out)


def discard_frames(sdk, cam, frame_count: int) -> None:
    """
    主动丢弃若干帧。

    修改曝光、增益、触发等参数后，图像流里可能还残留旧参数下的帧。
    丢弃几帧可以降低缓存帧对实验结果的干扰。
    """

    for _ in range(frame_count):
        _ = grab_one_frame_from_open_camera(sdk, cam)


def run_exposure_comparison(device_index: int = 0) -> None:
    """
    对多个曝光时间分别抓图并统计亮度。
    """

    import cv2

    sdk = load_hik_sdk()

    cam = None
    is_sdk_initialized = False
    is_handle_created = False
    is_device_opened = False
    is_grabbing = False

    try:
        sdk.MvCamera.MV_CC_Initialize()
        is_sdk_initialized = True

        device_list = sdk.MV_CC_DEVICE_INFO_LIST()
        tlayer_type = (
            sdk.MV_GIGE_DEVICE
            | sdk.MV_USB_DEVICE
            | sdk.MV_GENTL_CAMERALINK_DEVICE
            | sdk.MV_GENTL_CXP_DEVICE
            | sdk.MV_GENTL_XOF_DEVICE
        )

        ret = sdk.MvCamera.MV_CC_EnumDevices(tlayer_type, device_list)
        check_sdk_ret(ret, "枚举设备")

        if device_list.nDeviceNum == 0:
            raise RuntimeError(
                "没有发现相机。请先确认 MVS 能预览，且网卡和相机在同一网段。"
            )

        print_device_list(sdk, device_list)

        if device_index >= device_list.nDeviceNum:
            raise ValueError(f"设备序号 {device_index} 不存在。")

        cam = sdk.MvCamera()
        selected_device = cast(
            device_list.pDeviceInfo[device_index],
            POINTER(sdk.MV_CC_DEVICE_INFO),
        ).contents

        ret = cam.MV_CC_CreateHandle(selected_device)
        check_sdk_ret(ret, "创建相机句柄")
        is_handle_created = True

        ret = cam.MV_CC_OpenDevice(sdk.MV_ACCESS_Exclusive, 0)
        check_sdk_ret(ret, "打开设备")
        is_device_opened = True

        if selected_device.nTLayerType in (
            sdk.MV_GIGE_DEVICE,
            sdk.MV_GENTL_GIGE_DEVICE,
        ):
            packet_size = cam.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    print(f"警告：设置 GigE 包大小失败 ret[0x{ret:x}]")

        ret = cam.MV_CC_SetEnumValue("TriggerMode", sdk.MV_TRIGGER_MODE_OFF)
        check_sdk_ret(ret, "关闭触发模式")

        ret = cam.MV_CC_StartGrabbing()
        check_sdk_ret(ret, "开始取流")
        is_grabbing = True

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        print("\n=== 曝光时间对比 ===")

        for step_index, exposure_time_us in enumerate(EXPOSURE_TIMES_US, start=1):
            set_manual_exposure(cam, exposure_time_us)
            actual_exposure_time_us = get_current_exposure_time(sdk, cam)

            time.sleep(SETTLE_SECONDS)
            discard_frames(sdk, cam, DISCARD_FRAMES_AFTER_CHANGE)

            image = grab_one_frame_from_open_camera(sdk, cam)
            stats = calculate_image_stats(image)

            output_path = OUTPUT_DIR / (
                f"step{step_index:02d}_exposure_{int(exposure_time_us)}us.png"
            )
            saved = cv2.imwrite(str(output_path), image)
            if not saved:
                raise RuntimeError(f"保存图片失败：{output_path}")

            print(
                f"step={step_index:02d} | "
                f"set={exposure_time_us:.0f} us | "
                f"actual={actual_exposure_time_us:.2f} us | "
                f"mean={stats['mean_gray']:.2f} | "
                f"min={stats['min_gray']} | "
                f"max={stats['max_gray']} | "
                f"overexposed={stats['overexposed_ratio']:.2f}% | "
                f"saved={output_path}"
            )

    finally:
        if cam is not None and is_grabbing:
            cam.MV_CC_StopGrabbing()

        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()

        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()

        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()


if __name__ == "__main__":
    run_exposure_comparison(device_index=0)
