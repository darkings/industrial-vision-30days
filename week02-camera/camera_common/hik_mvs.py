from __future__ import annotations

import importlib
import os
import sys
from ctypes import POINTER, byref, c_ubyte, cast, memset, sizeof
from pathlib import Path


MVS_INSTALL_DIR = Path(r"C:\Program Files (x86)\MVS")


def find_mvimport_dir() -> Path:
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
        if (mvimport_dir / "MvCameraControl_class.py").exists():
            return mvimport_dir

    raise FileNotFoundError(
        "没有找到 MvCameraControl_class.py。请确认 MVS 已安装，"
        "并检查 MVCAM_COMMON_RUNENV 环境变量或 MVS_INSTALL_DIR。"
    )


def load_hik_sdk():
    mvimport_dir = find_mvimport_dir()
    if str(mvimport_dir) not in sys.path:
        sys.path.insert(0, str(mvimport_dir))
    return importlib.import_module("MvCameraControl_class")


def check_sdk_ret(ret: int, action: str) -> None:
    if ret != 0:
        raise RuntimeError(f"{action}失败，错误码 ret[0x{ret:x}]")


def decode_ctypes_string(ctypes_char_array) -> str:
    raw_bytes = memoryview(ctypes_char_array).tobytes()
    raw_bytes = raw_bytes.split(b"\x00", 1)[0]

    for encoding in ("gbk", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("latin-1", errors="replace")


def is_mono_pixel_format(sdk, pixel_type: int) -> bool:
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
    import cv2
    import numpy as np

    frame_info = frame_out.stFrameInfo
    width = frame_info.nWidth
    height = frame_info.nHeight
    src_pixel_type = frame_info.enPixelType

    if is_mono_pixel_format(sdk, src_pixel_type):
        dst_pixel_type = sdk.PixelType_Gvsp_Mono8
        channel_count = 1
    else:
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

    image = np.frombuffer(dst_buffer, dtype=np.uint8, count=dst_buffer_size)

    if channel_count == 1:
        return image.reshape((height, width)).copy()

    image = image.reshape((height, width, 3))
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def set_manual_exposure(cam, exposure_time_us: float) -> None:
    ret = cam.MV_CC_SetEnumValue("ExposureAuto", 0)
    check_sdk_ret(ret, "关闭自动曝光")

    ret = cam.MV_CC_SetFloatValue("ExposureTime", float(exposure_time_us))
    check_sdk_ret(ret, f"设置曝光时间 {exposure_time_us} us")


def get_current_exposure_time(sdk, cam) -> float:
    exposure_value = sdk.MVCC_FLOATVALUE()
    memset(byref(exposure_value), 0, sizeof(exposure_value))

    ret = cam.MV_CC_GetFloatValue("ExposureTime", exposure_value)
    check_sdk_ret(ret, "读取当前曝光时间")

    return float(exposure_value.fCurValue)


def grab_one_frame_from_open_camera(sdk, cam, timeout_ms: int = 1000):
    frame_out = sdk.MV_FRAME_OUT()
    memset(byref(frame_out), 0, sizeof(frame_out))

    ret = cam.MV_CC_GetImageBuffer(frame_out, timeout_ms)
    check_sdk_ret(ret, "抓取一帧")

    try:
        return convert_frame_to_numpy(sdk, cam, frame_out)
    finally:
        cam.MV_CC_FreeImageBuffer(frame_out)


def grab_one_frame(device_index: int = 0, exposure_time_us: float | None = None):
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
            raise RuntimeError("没有发现相机。请先确认 MVS 能预览，且网卡和相机在同一网段。")

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

        if selected_device.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            packet_size = cam.MV_CC_GetOptimalPacketSize()
            if int(packet_size) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
                if ret != 0:
                    print(f"警告：设置 GigE 包大小失败 ret[0x{ret:x}]")

        ret = cam.MV_CC_SetEnumValue("TriggerMode", sdk.MV_TRIGGER_MODE_OFF)
        check_sdk_ret(ret, "关闭触发模式")

        if exposure_time_us is not None:
            set_manual_exposure(cam, exposure_time_us)

        ret = cam.MV_CC_StartGrabbing()
        check_sdk_ret(ret, "开始取流")
        is_grabbing = True

        return grab_one_frame_from_open_camera(sdk, cam)

    finally:
        if cam is not None and is_grabbing:
            cam.MV_CC_StopGrabbing()
        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()
        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()
        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()
