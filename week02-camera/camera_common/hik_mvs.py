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
    candidate_dirs.append(Path(env_development_dir) / "Samples" / "Python" / "MvImport")

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


class HikCamera:
  """
  海康相机会话。

  进入 with 时打开相机并开始取流；在 with 内可以抓一帧或多帧；
  离开 with 时统一停止取流、关闭设备、销毁句柄、反初始化 SDK。
  """

  def __init__(
    self,
    device_index: int = 0,
    exposure_time_us: float | None = None,
    print_devices: bool = True,
  ) -> None:
    self.device_index = device_index
    self.exposure_time_us = exposure_time_us
    self.print_devices = print_devices

    self.sdk = None
    self.cam = None
    self.is_sdk_initialized = False
    self.is_handle_created = False
    self.is_device_opened = False
    self.is_grabbing = False

  def __enter__(self):
    self.sdk = load_hik_sdk()

    self.sdk.MvCamera.MV_CC_Initialize()
    self.is_sdk_initialized = True

    device_list = self.sdk.MV_CC_DEVICE_INFO_LIST()
    tlayer_type = (
      self.sdk.MV_GIGE_DEVICE
      | self.sdk.MV_USB_DEVICE
      | self.sdk.MV_GENTL_CAMERALINK_DEVICE
      | self.sdk.MV_GENTL_CXP_DEVICE
      | self.sdk.MV_GENTL_XOF_DEVICE
    )

    ret = self.sdk.MvCamera.MV_CC_EnumDevices(tlayer_type, device_list)
    check_sdk_ret(ret, "枚举设备")

    if device_list.nDeviceNum == 0:
      raise RuntimeError("没有发现相机。请先确认 MVS 能预览，且网卡和相机在同一网段。")

    if self.print_devices:
      print_device_list(self.sdk, device_list)

    if self.device_index >= device_list.nDeviceNum:
      raise ValueError(f"设备序号 {self.device_index} 不存在。")

    self.cam = self.sdk.MvCamera()
    selected_device = cast(
      device_list.pDeviceInfo[self.device_index],
      POINTER(self.sdk.MV_CC_DEVICE_INFO),
    ).contents

    ret = self.cam.MV_CC_CreateHandle(selected_device)
    check_sdk_ret(ret, "创建相机句柄")
    self.is_handle_created = True

    ret = self.cam.MV_CC_OpenDevice(self.sdk.MV_ACCESS_Exclusive, 0)
    check_sdk_ret(ret, "打开设备")
    self.is_device_opened = True

    if selected_device.nTLayerType in (
      self.sdk.MV_GIGE_DEVICE,
      self.sdk.MV_GENTL_GIGE_DEVICE,
    ):
      packet_size = self.cam.MV_CC_GetOptimalPacketSize()
      if int(packet_size) > 0:
        ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
        if ret != 0:
          print(f"警告：设置 GigE 包大小失败 ret[0x{ret:x}]")

    ret = self.cam.MV_CC_SetEnumValue("TriggerMode", self.sdk.MV_TRIGGER_MODE_OFF)
    check_sdk_ret(ret, "关闭触发模式")

    if self.exposure_time_us is not None:
      set_manual_exposure(self.cam, self.exposure_time_us)

    ret = self.cam.MV_CC_StartGrabbing()
    check_sdk_ret(ret, "开始取流")
    self.is_grabbing = True

    return self

  def __exit__(self, exc_type, exc_value, traceback) -> None:
    if self.cam is not None and self.is_grabbing:
      self.cam.MV_CC_StopGrabbing()
      self.is_grabbing = False

    if self.cam is not None and self.is_device_opened:
      self.cam.MV_CC_CloseDevice()
      self.is_device_opened = False

    if self.cam is not None and self.is_handle_created:
      self.cam.MV_CC_DestroyHandle()
      self.is_handle_created = False

    if self.sdk is not None and self.is_sdk_initialized:
      self.sdk.MvCamera.MV_CC_Finalize()
      self.is_sdk_initialized = False

  def grab_one_frame(self, timeout_ms: int = 1000):
    if self.sdk is None or self.cam is None or not self.is_grabbing:
      raise RuntimeError("相机尚未打开。请在 with HikCamera(...) as camera: 内调用。")

    return grab_one_frame_from_open_camera(self.sdk, self.cam, timeout_ms=timeout_ms)

  def discard_frames(self, n):
    if self.sdk is None or self.cam is None or not self.is_grabbing:
      raise RuntimeError("相机尚未打开。请在 with HikCamera(...) as camera: 内调用。")
    if n <= 0:
      return
    print(f"当前设置为:丢弃前{n}帧")
    for index in range(n):
      try:
        _ = grab_one_frame_from_open_camera(self.sdk, self.cam, timeout_ms=1000)
      except Exception as e:
        print(f"[!]警告 丢弃第{index + 1}发生异常：{e}")
    print("丢帧执行完毕！")

  def get_current_exposure_time(self) -> float:
    if self.sdk is None or self.cam is None:
      raise RuntimeError("相机尚未打开。请在 with HikCamera(...) as camera: 内调用。")

    return get_current_exposure_time(self.sdk, self.cam)

  def set_exposure_time(self, exposure_time_us: float) -> None:
    if self.cam is None or not self.is_device_opened:
      raise RuntimeError("相机尚未打开。请在 with HikCamera(...) as camera: 内调用。")
    set_manual_exposure(self.cam, exposure_time_us)

    self.exposure_time_us = exposure_time_us
    print(f"曝光时间已动态修改为：{exposure_time_us}")
