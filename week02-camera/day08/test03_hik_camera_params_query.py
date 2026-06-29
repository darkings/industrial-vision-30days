# -- coding: utf-8 --
"""
Day 8：海康工业相机参数查询练习。

本节目标：

1. 理解工业相机中常见参数的作用。
2. 学会用 SDK 读取 Float 类型参数，例如 ExposureTime、Gain。
3. 学会用 SDK 读取 Enum 类型参数，例如 TriggerMode、ExposureAuto。
4. 只查询参数，不修改参数，避免在学习阶段把相机状态改乱。

运行前注意：

1. MVS 软件可以用于确认相机能预览。
2. 运行 Python 脚本前，应关闭 MVS 或断开设备，避免相机被占用。
3. 当前没有固定支架和稳定光源，本节只学习参数含义，不做检测结论。
"""

from ctypes import POINTER, byref, cast, memset, sizeof
from pathlib import Path
import sys

# 让脚本无论是直接运行，还是被测试工具从项目根目录加载，
# 都能找到同目录下的 test01_hik_sdk_grab_one_frame.py。
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from test01_hik_sdk_grab_one_frame import (
    check_sdk_ret,
    load_hik_sdk,
    print_device_list,
)


def get_float_param(sdk, cam, param_name: str) -> None:
    """
    读取 Float 类型相机参数。

    Float 类型就是小数参数，例如：

    - ExposureTime：曝光时间，通常单位是微秒 us。
    - Gain：增益，通常单位是 dB 或相机厂商定义的增益值。
    - AcquisitionFrameRate：采集帧率。

    海康 SDK 需要先创建 MVCC_FLOATVALUE 结构体，
    然后把这个结构体传给 MV_CC_GetFloatValue() 填充。
    """

    float_value = sdk.MVCC_FLOATVALUE()
    memset(byref(float_value), 0, sizeof(float_value))

    ret = cam.MV_CC_GetFloatValue(param_name, float_value)

    if ret != 0:
        print(f"{param_name}: 读取失败 ret[0x{ret:x}]")
        return

    print(
        f"{param_name}: "
        f"当前值={float_value.fCurValue:.2f}, "
        f"最小值={float_value.fMin:.2f}, "
        f"最大值={float_value.fMax:.2f}"
    )


def get_enum_param(sdk, cam, param_name: str) -> None:
    """
    读取 Enum 类型相机参数。

    Enum 类型就是枚举参数，例如：

    - TriggerMode：触发模式，常见 Off / On。
    - ExposureAuto：自动曝光模式，常见 Off / Once / Continuous。
    - GainAuto：自动增益模式。
    - PixelFormat：像素格式，例如 Mono8、Bayer、RGB 等。

    这里先打印数值。后续我们再学习如何把数值解释成具体名称。
    """

    enum_value = sdk.MVCC_ENUMVALUE()
    memset(byref(enum_value), 0, sizeof(enum_value))

    ret = cam.MV_CC_GetEnumValue(param_name, enum_value)

    if ret != 0:
        print(f"{param_name}: 读取失败 ret[0x{ret:x}]")
        return

    print(f"{param_name}: 当前枚举值={enum_value.nCurValue}")


def query_camera_params(device_index: int = 0) -> None:
    """
    打开相机并查询当前参数。

    这个函数和抓一帧脚本的前半部分很像：

    初始化 SDK -> 枚举设备 -> 创建句柄 -> 打开设备 -> 查询参数 -> 释放资源

    区别是：本脚本不开始取流，也不抓图，只读参数。
    """

    sdk = load_hik_sdk()

    cam = None
    is_sdk_initialized = False
    is_handle_created = False
    is_device_opened = False

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

        print("\n=== Float 参数 ===")
        get_float_param(sdk, cam, "ExposureTime")
        get_float_param(sdk, cam, "Gain")
        get_float_param(sdk, cam, "AcquisitionFrameRate")
        get_float_param(sdk, cam, "ResultingFrameRate")

        print("\n=== Enum 参数 ===")
        get_enum_param(sdk, cam, "ExposureAuto")
        get_enum_param(sdk, cam, "GainAuto")
        get_enum_param(sdk, cam, "TriggerMode")
        get_enum_param(sdk, cam, "TriggerSource")
        get_enum_param(sdk, cam, "PixelFormat")

    finally:
        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()

        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()

        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()


if __name__ == "__main__":
    query_camera_params(device_index=0)
