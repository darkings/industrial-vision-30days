# camera/hik_sdk.py
from __future__ import annotations

import importlib
import os
import sys
from ctypes import POINTER, byref, c_ubyte, cast, memset, sizeof
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from core import CameraError, CameraOpenError


def check_sdk_ret(ret: int, action: str) -> None:
    """检查 SDK 返回码，若不为 0 则抛出 CameraError 异常"""
    if ret != 0:
        raise CameraError(f"{action}失败，SDK 错误码 [0x{ret:x}]")


class MVSLoader:
    """海康 MVS SDK Python 模块查找与加载器"""

    @staticmethod
    def find_mvimport_dir(mvs_install_dir: Path | None) -> Path:
        """查找 MvImport 所在目录"""
        env_development_dir = os.getenv("MVCAM_COMMON_RUNENV")
        candidate_dirs: list[Path] = []
        if mvs_install_dir is not None:
            candidate_dirs.append(
                mvs_install_dir / "Development" / "Samples" / "Python" / "MvImport"
            )
        else:
            if env_development_dir:
                candidate_dirs.append(
                    Path(env_development_dir) / "Samples" / "Python" / "MvImport"
                )
            candidate_dirs.append(
                Path(r"C:\Program Files (x86)\MVS") / "Samples" / "Python" / "MvImport"
            )
        for mvimport_dir in candidate_dirs:
            if (mvimport_dir / "MvCameraControl_class.py").exists():
                return mvimport_dir

        raise CameraOpenError(
            "未找到 MVS SDK 文件，请检查 MVS 安装路径或 MVCAM_COMMON_RUNENV 环境变量"
        )

    @classmethod
    def load_sdk(cls, mvs_install_dir: Path | None) -> Any:
        """动态加载 MvCameraControl_class 模块"""
        mvimport_dir = cls.find_mvimport_dir(mvs_install_dir)
        if str(mvimport_dir) not in sys.path:
            sys.path.insert(0, str(mvimport_dir))
        return importlib.import_module("MvCameraControl_class")


class HikCameraSDKDevice:
    """底层 SDK 设备封装类，管理相机生命周期与原生 Buffer 提取"""

    def __init__(self, mvs_install_dir: Path | None, logger: Any | None = None) -> None:
        self.mvs_install_dir = mvs_install_dir

        self.logger = logger
        self.sdk = MVSLoader.load_sdk(self.mvs_install_dir)
        self.is_sdk_initialized = False
        self.cam_handle: Any | None = None
        self.is_open: bool = False
        self.is_grabbing: bool = False
        ret = self.sdk.MvCamera.MV_CC_Initialize()
        check_sdk_ret(ret, "初始化 MVS SDK")
        self.is_sdk_initialized = True

    def _extract_sn(self, dev_info: Any) -> str:
        """从设备结构体中提取序列号 (SN)"""
        gentl_gige = getattr(self.sdk, "MV_GENTL_GIGE_DEVICE", None)
        usb_device = getattr(self.sdk, "MV_USB_DEVICE", None)

        if dev_info.nTLayerType in (self.sdk.MV_GIGE_DEVICE, gentl_gige):
            raw = memoryview(dev_info.SpecialInfo.stGigEInfo.chSerialNumber).tobytes()
        elif usb_device and dev_info.nTLayerType == usb_device:
            raw = memoryview(dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber).tobytes()
        else:
            return ""

        return raw.split(b"\x00", 1)[0].decode("utf-8", errors="ignore").strip()

    def find_device_by_sn(self, serial_number: str) -> Any | None:
        """按序列号枚举并匹配相机的设备信息结构体"""
        device_list = self.sdk.MV_CC_DEVICE_INFO_LIST()
        memset(byref(device_list), 0, sizeof(device_list))

        tlayer = (
            self.sdk.MV_GIGE_DEVICE
            | self.sdk.MV_USB_DEVICE
            | getattr(self.sdk, "MV_GENTL_GIGE_DEVICE", 0)
        )
        ret = self.sdk.MvCamera.MV_CC_EnumDevices(tlayer, device_list)
        check_sdk_ret(ret, "枚举设备")

        target_sn = serial_number.strip().lower()
        for i in range(int(device_list.nDeviceNum)):
            p_dev_info = cast(
                device_list.pDeviceInfo[i], POINTER(self.sdk.MV_CC_DEVICE_INFO)
            )
            dev_info = p_dev_info.contents
            sn = self._extract_sn(dev_info)

            if sn.lower() == target_sn:
                return dev_info

        return None

    def open_by_sn(self, serial_number: str) -> None:
        """根据序列号选择设备、创建句柄并打开相机"""
        device_info = self.find_device_by_sn(serial_number)
        if device_info is None:
            raise CameraOpenError(f"未匹配到序列号为 [{serial_number}] 的海康相机设备")

        # 1. 创建句柄
        self.cam_handle = self.sdk.MvCamera()
        ret = self.cam_handle.MV_CC_CreateHandle(device_info)
        check_sdk_ret(ret, "创建相机句柄")

        # 2. 打开设备
        ret = self.cam_handle.MV_CC_OpenDevice(self.sdk.MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self.cam_handle.MV_CC_DestroyHandle()
            self.cam_handle = None
            check_sdk_ret(ret, f"打开相机设备 [SN: {serial_number}]")

        self.is_open = True

    def set_exposure_and_trigger(self, exposure_us: float) -> None:
        """关闭自动曝光，设置曝光时间，并将触发模式设置为关闭 (TriggerMode=OFF)"""

        # 关闭自动曝光并设置微秒曝光值
        ret = self.cam_handle.MV_CC_SetEnumValue("ExposureAuto", 0)
        check_sdk_ret(ret, "关闭自动曝光")

        ret = self.cam_handle.MV_CC_SetFloatValue("ExposureTime", float(exposure_us))
        check_sdk_ret(ret, f"设置曝光时间 [{exposure_us} us]")

        # 设置 TriggerMode = OFF (关闭触发模式)
        ret = self.cam_handle.MV_CC_SetEnumValue("TriggerMode", 0)
        check_sdk_ret(ret, "关闭触发模式 (TriggerMode=OFF)")

    def start_grabbing(self) -> None:
        """开启采集流"""
        if not self.is_grabbing:
            ret = self.cam_handle.MV_CC_StartGrabbing()
            check_sdk_ret(ret, "开启采集流")
            self.is_grabbing = True

    def stop_grabbing(self) -> None:
        """停止采集流"""
        if self.is_grabbing and self.cam_handle:
            try:
                self.cam_handle.MV_CC_StopGrabbing()
            except Exception as e:  # noqa: BLE001
                if self.logger:
                    self.logger.warning("停止采集流异常: %s", e)
            finally:
                self.is_grabbing = False

    def discard_frames(self, count: int) -> None:
        """抓取并丢弃指定数量的初始缓存帧"""
        temp_frame = self.sdk.MV_FRAME_OUT()
        for _ in range(count):
            memset(byref(temp_frame), 0, sizeof(temp_frame))
            ret = self.cam_handle.MV_CC_GetImageBuffer(temp_frame, 500)
            if ret == 0:
                self.cam_handle.MV_CC_FreeImageBuffer(temp_frame)

    def grab_one_frame_and_convert(
        self, timeout_ms: int = 1000
    ) -> tuple[np.ndarray, str]:
        """
        抓取一帧图像，转换为标准的 NumPy 格式，并在 finally 中安全释放 SDK 缓存 Buffer。
        返回包含深拷贝图像矩阵与颜色空间标识的元组。
        """
        frame_out = self.sdk.MV_FRAME_OUT()
        memset(byref(frame_out), 0, sizeof(frame_out))

        ret = self.cam_handle.MV_CC_GetImageBuffer(frame_out, timeout_ms)
        check_sdk_ret(ret, "获取图像 Buffer")

        try:
            frame_info = frame_out.stFrameInfo
            width, height = frame_info.nWidth, frame_info.nHeight
            src_type = frame_info.enPixelType

            is_mono = src_type in (
                self.sdk.PixelType_Gvsp_Mono8,
                self.sdk.PixelType_Gvsp_Mono10,
                self.sdk.PixelType_Gvsp_Mono10_Packed,
                self.sdk.PixelType_Gvsp_Mono12,
                self.sdk.PixelType_Gvsp_Mono12_Packed,
                self.sdk.PixelType_Gvsp_Mono14,
                self.sdk.PixelType_Gvsp_Mono16,
            )

            dst_type = (
                self.sdk.PixelType_Gvsp_Mono8
                if is_mono
                else self.sdk.PixelType_Gvsp_RGB8_Packed
            )
            channels = 1 if is_mono else 3
            dst_size = width * height * channels
            dst_buf = (c_ubyte * dst_size)()

            convert_param = self.sdk.MV_CC_PIXEL_CONVERT_PARAM_EX()
            memset(byref(convert_param), 0, sizeof(convert_param))
            convert_param.nWidth = width
            convert_param.nHeight = height
            convert_param.pSrcData = frame_out.pBufAddr
            convert_param.nSrcDataLen = frame_info.nFrameLen
            convert_param.enSrcPixelType = src_type
            convert_param.enDstPixelType = dst_type
            convert_param.pDstBuffer = dst_buf
            convert_param.nDstBufferSize = dst_size

            ret = self.cam_handle.MV_CC_ConvertPixelTypeEx(convert_param)
            check_sdk_ret(ret, "转换像素格式")

            raw_arr = np.frombuffer(dst_buf, dtype=np.uint8, count=dst_size)

            if is_mono:
                return raw_arr.reshape((height, width)).copy(), "GRAY"
            else:
                bgr_img = cv2.cvtColor(
                    raw_arr.reshape((height, width, 3)), cv2.COLOR_RGB2BGR
                )
                return bgr_img.copy(), "BGR"

        finally:
            self.cam_handle.MV_CC_FreeImageBuffer(frame_out)

    def close(self) -> None:
        """关闭相机并按严格的逆序释放底层资源"""

        # 1. 停止取流
        self.stop_grabbing()

        # 2. 关闭设备
        if self.cam_handle and self.is_open:
            try:
                self.cam_handle.MV_CC_CloseDevice()
            except Exception as exc:  # noqa: BLE001
                if self.logger:
                    self.logger.warning("关闭相机设备异常: %s", exc)

            finally:
                self.is_open = False

        # 3. 销毁句柄
        if self.cam_handle:
            try:
                self.cam_handle.MV_CC_DestroyHandle()
            except Exception as exc:  # noqa: BLE001
                if self.logger:
                    self.logger.warning("销毁句柄异常: %s", exc)
            finally:
                self.cam_handle = None

        # 4. 清空 SDK 引用
        if self.sdk is not None and self.is_sdk_initialized:
            self.sdk.MvCamera.MV_CC_Finalize()
            self.is_sdk_initialized = False
