"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-29 09:04:35
LastEditTime: 2026-06-29 09:05:12
"""

# 寻找SDK目录
import importlib
import os
import sys
from ctypes import POINTER, byref, c_ubyte, cast, memset, sizeof
from pathlib import Path

MVS_INSTALL_DIR = Path(r"C:\Program Files (x86)\MVS")
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "grab_one_frame"
OUTPUT_IMAGE_PATH = OUTPUT_DIR / "hik_grab_one_frame.png"


def find_mvimport_dir() -> Path:
    sdk_dirs = []
    # 读取系统变量
    env_development = os.getenv("MVCAM_COMMON_RUNENV")

    # 判断变量是否存在
    if env_development:
        print(f"MVS路径存在与系统变量中：{env_development}")
        sdk_dirs.append(
            Path(env_development) / "Samples" / "Python" / "MvImport",
        )

    # 添加第二条默认路径
    sdk_dirs.append(
        Path(MVS_INSTALL_DIR) / "Development" / "Samples" / "Python" / "MvImport",
    )
    # 循环存放的路径数组
    for path in sdk_dirs:
        sdk_path = path / "MvCameraControl_class.py"
        # 只要找到立即返回
        if sdk_path.exists():
            return path
    # 运行到这里表示2个路径都没有找到,直接抛出异常
    raise FileNotFoundError("没有找到海康SDK文件，请确认MVS已安装！")


# 导入SDK封装模块
def load_hk_sdk():
    # 当前sdk目录
    sdk_dir = find_mvimport_dir()
    # 判断sdk是否已经导入
    if str(sdk_dir) not in sys.path:
        # 如果不在就导入它。并把它放在第一位
        sys.path.insert(0, str(sdk_dir))

    # 返回并导入的SDK模块
    return importlib.import_module("MvCameraControl_class")


# 统一海康SDK函数错误拦截器
def check_hk_ret(ret: int, action: str):
    if ret != 0:
        raise RuntimeError(f"{action}异常，错误码 ret[0x{ret:x}]")


# 将C语言字符数组转换为Python字符串
def decode_ctypes_string(ctypes_char_array) -> str:
    # 先把传递过来的ctypes_char_array使用memoryview从内存中抠出来转化为字符串
    raw_bytes = memoryview(ctypes_char_array).tobytes()
    # 截断x00后买你无意义数据
    raw_bytes = raw_bytes.split(b"\x00", 1)[0]
    # 循环转码错误 ，哪个成功返回哪个
    for ending in ("gbk", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(ending)
        except UnicodeDecodeError:
            # 捕获异常后，继续循环下一个
            continue
    # 最终都没有转码成功后，将非法字符转化为空返回
    return raw_bytes.decode("latin-1", errors="replace")


# 判断当前图像是不是黑白模式
def is_mono_pixel_format(sdk, pixel_type: int) -> bool:
    # sdk中常用的黑白常量
    mono_format = {
        sdk.PixelType_Gvsp_Mono8,
        sdk.PixelType_Gvsp_Mono10,
        sdk.PixelType_Gvsp_Mono10_Packed,
        sdk.PixelType_Gvsp_Mono12,
        sdk.PixelType_Gvsp_Mono12_Packed,
        sdk.PixelType_Gvsp_Mono14,
        sdk.PixelType_Gvsp_Mono16,
    }
    # 如果传递的pixel_type在这些常量里返回True否则返回false
    return pixel_type in mono_format


# 解析并打印局域网所有相机信息
def print_device_list(sdk, device_list) -> None:
    # 发现相机数量
    print(f"发现相机数量：{device_list.nDeviceNum}")

    # 循环相机列表
    for index in range(device_list.nDeviceNum):
        # 当前相机信息
        device_info = cast(
            device_list.pDeviceInfo[index], POINTER(sdk.MV_CC_DEVICE_INFO)
        ).contents

        # 判断当前设备协议类型
        if device_info.nTLayerType in (sdk.MV_GIGE_DEVICE, sdk.MV_GENTL_GIGE_DEVICE):
            # 获取网口信息
            gige_info = device_info.SpecialInfo.stGigEInfo
            # 获取型号和序列表
            modal_name = decode_ctypes_string(gige_info.chModelName)
            serial_number = decode_ctypes_string(gige_info.chSerialNumber)
            # 获取IPV4地址
            ip1 = (gige_info.nCurrentIp & 0xFF000000) >> 24
            ip2 = (gige_info.nCurrentIp & 0x00FF0000) >> 16
            ip3 = (gige_info.nCurrentIp & 0x0000FF00) >> 8
            ip4 = gige_info.nCurrentIp & 0x000000FF

            # 打印结果：
            print(
                f"[{index}] GigE 相机\n"
                f"型号：{modal_name}\n"
                f"序列号：{serial_number}\n"
                f"ip地址：{ip1}.{ip2}.{ip3}.{ip4}"
            )
        else:
            print(f"[{index}]非GigE设备")


# 转化为numpy.ndarray
def convert_frame_to_numpy(sdk, cam, frame_out):
    import cv2
    import numpy as np

    # 获取相机抓拍元数据的信息
    frame_info = frame_out.stFrameInfo
    width = frame_info.nWidth
    height = frame_info.nHeight
    src_pixel_type = frame_info.enPixelType

    # 判断图像类型
    is_mono = is_mono_pixel_format(sdk, src_pixel_type)

    channel_count = 0
    if is_mono:
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
    check_hk_ret(ret, "转换像素格式")

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


# 相机生命周期
def grab_one_frame(device_index: int = 0) -> None:
    # 1.加载SDK
    sdk = load_hk_sdk()

    cam = None
    is_sdk_initialized = False
    is_handle_created = False
    is_device_opened = False
    is_grabbing = False

    try:
        # 2. 初始化SDK
        sdk.MvCamera.MV_CC_Initialize()
        is_sdk_initialized = True
        # sdk 版本
        sdk_version = sdk.MvCamera.MV_CC_GetSDKVersion()
        print(f"SDK版本：0x{sdk_version:x}")

        # 3. 获取相机
        # 设备列表
        device_list = sdk.MV_CC_DEVICE_INFO_LIST()
        # 相机传输协议类型
        tlayer_type = (
            sdk.MV_GIGE_DEVICE
            | sdk.MV_USB_DEVICE
            | sdk.MV_GENTL_CAMERALINK_DEVICE
            | sdk.MV_GENTL_CXP_DEVICE
            | sdk.MV_GENTL_XOF_DEVICE
        )
        ret = sdk.MvCamera.MV_CC_EnumDevices(tlayer_type, device_list)
        check_hk_ret(ret, "枚举相机设备")
        # 如果相机为0
        if device_list.nDeviceNum == 0:
            raise RuntimeError("相机设备为0，请确认相机已连接")
        # 相机列表
        print_device_list(sdk, device_list)
        # 获取相机
        cam = sdk.MvCamera()
        selected_device = cast(
            device_list.pDeviceInfo[device_index],
            POINTER(sdk.MV_CC_DEVICE_INFO),
        ).contents

        # 4.创建相机句柄
        ret = cam.MV_CC_CreateHandle(selected_device)
        check_hk_ret(ret, "创建相机句柄")
        is_handle_created = True

        # 5.打开相机
        ret = cam.MV_CC_OpenDevice(sdk.MV_ACCESS_Exclusive, 0)

        check_hk_ret(ret, "打开设备")
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
                else:
                    print(f"已设置 GigE 最佳包大小：{packet_size}")
            else:
                print(f"警告：获取 GigE 最佳包大小失败 ret[0x{packet_size:x}]")

        # 6.采集图像
        ret = cam.MV_CC_SetEnumValue("TriggerMode", sdk.MV_TRIGGER_MODE_OFF)
        check_hk_ret(ret, "关闭触发模式")
        ret = cam.MV_CC_StartGrabbing()
        check_hk_ret(ret, "开始取流")
        is_grabbing = True
        frame_out = sdk.MV_FRAME_OUT()
        memset(byref(frame_out), 0, sizeof(frame_out))

        ret = cam.MV_CC_GetImageBuffer(frame_out, 1000)
        check_hk_ret(ret, "抓取一帧")
        try:
            print(
                "抓到一帧："
                f"宽度={frame_out.stFrameInfo.nWidth}, "
                f"高度={frame_out.stFrameInfo.nHeight}, "
                f"帧号={frame_out.stFrameInfo.nFrameNum}, "
                f"像素格式={frame_out.stFrameInfo.enPixelType}"
            )
            # 7.转换为numpy.ndarray
            image = convert_frame_to_numpy(sdk, cam, frame_out)
            # 8.保存图像
            import cv2

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            saved = cv2.imwrite(str(OUTPUT_IMAGE_PATH), image)
            if not saved:
                raise RuntimeError("图片保存失败")
        finally:
            cam.MV_CC_FreeImageBuffer(frame_out)
    finally:
        # 9，停止取流
        if cam is not None and is_grabbing:
            cam.MV_CC_StopGrabbing()
        # 10.关闭相机
        if cam is not None and is_device_opened:
            cam.MV_CC_CloseDevice()
        # 11.销毁相机句柄
        if cam is not None and is_handle_created:
            cam.MV_CC_DestroyHandle()
        # 12.相机sdk反初始化
        if is_sdk_initialized:
            sdk.MvCamera.MV_CC_Finalize()


grab_one_frame()
