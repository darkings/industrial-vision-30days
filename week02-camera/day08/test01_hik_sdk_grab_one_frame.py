# -- coding: utf-8 --
"""
Day 8：海康 MVS SDK 抓取一帧图像学习骨架。

本文件的学习目标不是立刻做稳定检测，而是看懂工业相机 SDK 的基本流程：

1. 找到 MVS 安装目录中的 Python SDK 导入文件。
2. 初始化 SDK。
3. 枚举当前电脑能发现的工业相机。
4. 打开指定相机。
5. 设置 GigE 相机推荐包大小和连续采集模式。
6. 开始取流并抓取一帧。
7. 把 SDK 返回的图像 buffer 转成 OpenCV 可处理的 numpy.ndarray。
8. 保存图片。
9. 停止取流、关闭设备、销毁句柄、反初始化 SDK。

当前 Windows 电脑上的 MVS 安装路径：
C:\\Program Files (x86)\\MVS
"""

from __future__ import annotations

import importlib
import os
import sys
from ctypes import POINTER, byref, c_ubyte, cast, memset, sizeof
from pathlib import Path


# 当前 Windows 电脑上的 MVS 安装根目录。
# 注意：Program Files (x86) 中间有空格，写路径时必须用字符串或 Path，不能手动省略空格。
MVS_INSTALL_DIR = Path(r"C:\Program Files (x86)\MVS")

# 输出目录放在当前 day08 目录下，方便保留本节课的抓帧结果。
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "grab_one_frame"
OUTPUT_IMAGE_PATH = OUTPUT_DIR / "hik_grab_one_frame.png"


def find_mvimport_dir() -> Path:
    """
    找到海康 Python SDK 的 MvImport 目录。

    MVS 安装后通常会设置环境变量：

    MVCAM_COMMON_RUNENV=C:\\Program Files (x86)\\MVS\\Development

    海康官方 Python 示例会根据这个环境变量拼出：

    C:\\Program Files (x86)\\MVS\\Development\\Samples\\Python\\MvImport

    这个目录里最重要的文件是：

    MvCameraControl_class.py

    它用 ctypes 封装了海康 C/C++ SDK，让 Python 可以调用
    MV_CC_EnumDevices、MV_CC_OpenDevice、MV_CC_GetImageBuffer 等函数。
    """

    env_development_dir = os.getenv("MVCAM_COMMON_RUNENV")

    candidate_dirs = []

    if env_development_dir:
        candidate_dirs.append(
            Path(env_development_dir) / "Samples" / "Python" / "MvImport"
        )

    candidate_dirs.append(
        MVS_INSTALL_DIR / "Development" / "Samples" / "Python" / "MvImport"
    )

    for mvimport_dir in candidate_dirs:
        sdk_file = mvimport_dir / "MvCameraControl_class.py"
        if sdk_file.exists():
            return mvimport_dir

    raise FileNotFoundError(
        "没有找到 MvCameraControl_class.py。请确认 MVS 已安装，"
        "并检查 MVCAM_COMMON_RUNENV 环境变量或 MVS_INSTALL_DIR。"
    )


def load_hik_sdk():
    """
    导入海康 SDK 的 Python 封装模块。

    普通第三方包通常用 pip 安装，然后直接 import。
    但海康 MVS 的 Python SDK 文件在 MVS 安装目录里，不在当前项目里，
    所以需要先把 MvImport 目录加入 sys.path。
    """

    mvimport_dir = find_mvimport_dir()

    # sys.path 是 Python 查找模块的路径列表。
    # 把 MvImport 放到最前面后，importlib 才能找到 MvCameraControl_class.py。
    if str(mvimport_dir) not in sys.path:
        sys.path.insert(0, str(mvimport_dir))

    return importlib.import_module("MvCameraControl_class")


def check_sdk_ret(ret: int, action: str) -> None:
    """
    检查海康 SDK 函数返回值。

    海康 SDK 的很多函数返回 0 表示成功，非 0 表示失败。
    失败时通常会返回十六进制错误码，例如 0x80000000 这一类。
    """

    if ret != 0:
        raise RuntimeError(f"{action}失败，错误码 ret[0x{ret:x}]")


def decode_ctypes_string(ctypes_char_array) -> str:
    """
    把 SDK 结构体中的 C 字符数组转换成 Python 字符串。

    SDK 里设备型号、序列号等字段不是普通 Python str，
    而是 ctypes 字符数组，里面可能包含 \\x00 结尾符。
    """

    raw_bytes = memoryview(ctypes_char_array).tobytes()
    raw_bytes = raw_bytes.split(b"\x00", 1)[0]

    for encoding in ("gbk", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("latin-1", errors="replace")


def is_mono_pixel_format(sdk, pixel_type: int) -> bool:
    """
    判断当前图像是不是黑白图像格式。

    黑白相机常见格式是 Mono8、Mono10、Mono12 等。
    学习阶段最希望拿到 Mono8，因为它可以直接变成二维灰度图：

    shape = (height, width)
    """

    mono_formats = (
        sdk.PixelType_Gvsp_Mono8,
        sdk.PixelType_Gvsp_Mono10,
        sdk.PixelType_Gvsp_Mono10_Packed,
        sdk.PixelType_Gvsp_Mono12,
        sdk.PixelType_Gvsp_Mono12_Packed,
        sdk.PixelType_Gvsp_Mono14,
        sdk.PixelType_Gvsp_Mono16,
    )

    return pixel_type in mono_formats


def print_device_list(sdk, device_list) -> None:
    """
    打印枚举到的相机信息，方便确认 Python 找到的是哪台设备。

    对 GigE 相机，重点看：
    - 设备序号
    - 型号
    - 序列号
    - 当前 IP
    """

    print(f"发现设备数量：{device_list.nDeviceNum}")

    for index in range(device_list.nDeviceNum):
        device_info = cast(
            device_list.pDeviceInfo[index],
            POINTER(sdk.MV_CC_DEVICE_INFO),
        ).contents

        if device_info.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            gige_info = device_info.SpecialInfo.stGigEInfo
            model_name = decode_ctypes_string(gige_info.chModelName)
            serial_number = decode_ctypes_string(gige_info.chSerialNumber)

            ip1 = (gige_info.nCurrentIp & 0xFF000000) >> 24
            ip2 = (gige_info.nCurrentIp & 0x00FF0000) >> 16
            ip3 = (gige_info.nCurrentIp & 0x0000FF00) >> 8
            ip4 = gige_info.nCurrentIp & 0x000000FF

            print(f"[{index}] GigE 相机")
            print(f"    型号：{model_name}")
            print(f"    序列号：{serial_number}")
            print(f"    当前 IP：{ip1}.{ip2}.{ip3}.{ip4}")
        else:
            print(f"[{index}] 非 GigE 设备，传输层类型：{device_info.nTLayerType}")


def convert_frame_to_numpy(sdk, cam, frame_out):
    """
    把 SDK 抓到的一帧图像转换成 numpy.ndarray。

    SDK 抓到的是一段图像内存 buffer，不是 OpenCV 图片。
    OpenCV 能处理的是 numpy.ndarray，所以必须做两步：

    1. 使用 MV_CC_ConvertPixelTypeEx 转换像素格式。
    2. 使用 np.frombuffer 把 ctypes buffer 转成 numpy 数组。
    """

    # cv2 和 numpy 只有在真正处理图像时才需要。
    # 这样做的好处是：单独检查 MVS SDK 路径时，不会因为 OpenCV 环境没装好而失败。
    import cv2
    import numpy as np

    frame_info = frame_out.stFrameInfo
    width = frame_info.nWidth
    height = frame_info.nHeight
    src_pixel_type = frame_info.enPixelType

    is_mono = is_mono_pixel_format(sdk, src_pixel_type)

    if is_mono:
        dst_pixel_type = sdk.PixelType_Gvsp_Mono8
        channel_count = 1
    else:
        # 海康示例通常把彩色图转成 RGB8。
        # OpenCV 默认使用 BGR，如果后续发现颜色反了，再用 cv2.cvtColor 转换。
        dst_pixel_type = sdk.PixelType_Gvsp_RGB8_Packed
        channel_count = 3

    dst_buffer_size = width * height * channel_count
    dst_buffer = (c_ubyte * dst_buffer_size)()

    convert_param = sdk.MV_CC_PIXEL_CONVERT_PARAM_EX()
    memset(byref(convert_param), 0, sizeof(convert_param))

    convert_param.nWidth = width
    convert_param.nHeight = height
    convert_param.pSrcData = frame_out.pBufAddr
    convert_param.nSrcDataLen = frame_info.nFrameLen
    convert_param.enSrcPixelType = src_pixel_type
    convert_param.enDstPixelType = dst_pixel_type
    convert_param.pDstBuffer = dst_buffer
    convert_param.nDstBufferSize = dst_buffer_size

    ret = cam.MV_CC_ConvertPixelTypeEx(convert_param)
    check_sdk_ret(ret, "转换像素格式")

    image = np.frombuffer(
        dst_buffer,
        dtype=np.uint8,
        count=dst_buffer_size,
    )

    if channel_count == 1:
        image = image.reshape((height, width))
    else:
        image = image.reshape((height, width, 3))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


def grab_one_frame(device_index: int = 0) -> None:
    """
    打开相机并抓取一帧图片。

    device_index 表示选择第几台枚举到的设备。
    如果只接了一台相机，一般就是 0。
    """

    sdk = load_hik_sdk()

    cam = None
    is_sdk_initialized = False
    is_handle_created = False
    is_device_opened = False
    is_grabbing = False

    try:
        # 初始化 SDK。使用 SDK 前先初始化，程序结束前要反初始化。
        sdk.MvCamera.MV_CC_Initialize()
        is_sdk_initialized = True

        sdk_version = sdk.MvCamera.MV_CC_GetSDKVersion()
        print(f"SDK 版本：0x{sdk_version:x}")

        device_list = sdk.MV_CC_DEVICE_INFO_LIST()

        # 枚举传输层类型。
        # 当前相机是 GigE，所以 MV_GIGE_DEVICE 是重点。
        # 这里保留 USB、GenTL 等类型，是为了和官方示例保持兼容。
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
            raise RuntimeError("没有发现相机。请先确认 MVS 能预览，且网卡和相机在可通信网段。")

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

        # GigE 相机建议设置最佳网络包大小。
        # 包大小合适时，网口传输效率更高，丢包风险更低。
        if selected_device.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            packet_size = cam.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    print(f"警告：设置 GigE 包大小失败 ret[0x{ret:x}]")
            else:
                print(f"警告：获取 GigE 最佳包大小失败 ret[0x{packet_size:x}]")

        # 当前阶段先使用连续采集，所以关闭触发模式。
        # 后面做工业项目时，可能会改成硬件触发。
        ret = cam.MV_CC_SetEnumValue("TriggerMode", sdk.MV_TRIGGER_MODE_OFF)
        check_sdk_ret(ret, "关闭触发模式")

        ret = cam.MV_CC_StartGrabbing()
        check_sdk_ret(ret, "开始取流")
        is_grabbing = True

        frame_out = sdk.MV_FRAME_OUT()
        memset(byref(frame_out), 0, sizeof(frame_out))

        # 等待最多 1000 ms 抓取一帧。
        ret = cam.MV_CC_GetImageBuffer(frame_out, 1000)
        check_sdk_ret(ret, "抓取一帧")

        try:
            print(
                "抓到一帧："
                f"宽度={frame_out.stFrameInfo.nWidth}, "
                f"高度={frame_out.stFrameInfo.nHeight}, "
                f"帧号={frame_out.stFrameInfo.nFrameNum}, "
                f"像素格式={frame_out.stFrameInfo.enPixelType}"
            )

            image = convert_frame_to_numpy(sdk, cam, frame_out)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            import cv2

            saved = cv2.imwrite(str(OUTPUT_IMAGE_PATH), image)

            if not saved:
                raise RuntimeError(f"保存图片失败：{OUTPUT_IMAGE_PATH}")

            print(f"保存成功：{OUTPUT_IMAGE_PATH}")
            print(f"OpenCV 图像 shape：{image.shape}")
        finally:
            # 使用 MV_CC_GetImageBuffer 取到图后，必须释放 buffer。
            # 不释放会导致 SDK 内部缓存被占住，连续抓图时容易出问题。
            cam.MV_CC_FreeImageBuffer(frame_out)

    finally:
        # 释放资源要反向执行：
        # 先停止取流，再关闭设备，再销毁句柄，最后反初始化 SDK。
        if cam is not None and is_grabbing:
            cam.MV_CC_StopGrabbing()

        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()

        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()

        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()


if __name__ == "__main__":
    # 如果只接了一台相机，通常使用设备序号 0。
    # 如果枚举出多台相机，可以把这里改成 1、2 等。
    grab_one_frame(device_index=0)
