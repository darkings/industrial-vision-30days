# camera/hik_camera.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from core.exceptions import CameraError, CameraOpenError, CameraReadError

from camera.hik_sdk import HikCameraSDKDevice
from camera.image_source import ImageInput, ImageSource


class HikCameraSource(ImageSource):
    """海康相机 ImageSource 规范实现类"""

    def __init__(
        self,
        camera_config: Any,  # CameraConfig 相机配置对象
        product: Any,  # KeycapProduct 键帽产品对象
        batch_id: str,
        logger: Any | None = None,
    ) -> None:
        self.config = camera_config
        self.product = product
        self.batch_id = batch_id
        self.logger = logger
        self.device: HikCameraSDKDevice | None = None
        self._opened: bool = False
        self._frame_count: int = 0

    @property
    def is_opened(self) -> bool:
        return self._opened

    def open(self) -> None:
        """
        初始化并打开相机。
        只有当所有配置与前 5 帧丢帧完全成功后，才可将 _opened 置为 True。
        """
        if self._opened:
            return

        try:
            self.device = HikCameraSDKDevice(
                mvs_install_dir=self.config.mvs_install_dir, logger=self.logger
            )

            # 1. 根据序列号匹配并打开设备
            sn = self.config.serial_number
            self.device.open_by_sn(sn)

            # 2. 设置正式基线曝光 (1200us) 及 TriggerMode=OFF
            exposure_us = getattr(self.config, "exposure_us", 1200.0)
            self.device.set_exposure_and_trigger(exposure_us)

            # 3. 开启取流
            self.device.start_grabbing()

            # 4. 丢弃初始 5 帧缓存帧，保证画质稳定
            discard_frames = getattr(self.config, "discard_frames", 5)
            self.device.discard_frames(discard_frames)

            # 关键规则：只有完全无误初始化后，才标志 _opened = True
            self._opened = True
            self._frame_count = 0

            if self.logger:
                self.logger.info("海康相机 [SN: %s] 成功初始化并开流", sn)

        except Exception as err:
            self.close()  # 若部分步骤初始化失败，执行逆序资源清理
            if isinstance(err, (CameraOpenError, CameraError)):
                raise CameraOpenError(
                    f"无法打开相机 [SN: {self.config.serial_number}]: {err}"
                ) from err
            raise CameraOpenError(f"打开相机时发生未知错误: {err}") from err

    def close(self) -> None:
        """关闭相机。支持部分初始化安全清理以及幂等重复调用。"""
        self._opened = False
        if self.device:
            try:
                # 设备内部会按照逆序自动释放：停止取流 -> 关闭设备 -> 销毁句柄 -> 释放 SDK
                self.device.close()
            except Exception as exc:  # noqa: BLE001
                if self.logger:
                    self.logger.warning("关闭海康相机时发生异常: %s", exc)
            finally:
                self.device = None

        if self.logger:
            self.logger.info(
                "海康相机 [SN: %s] 资源已安全释放", self.config.serial_number
            )

    def read(self, timeout_ms: int = 1000) -> ImageInput:
        """
        抓取一帧图像并封装为 ImageInput 标准对象。
        超时或失败时抛出 CameraReadError 异常，绝不返回 None。
        """
        if not self._opened or not self.device:
            raise CameraReadError(
                f"相机 [SN: {self.config.serial_number}] 未处于就绪状态"
            )

        try:
            # 抓取图像与格式（底层已自动执行 .copy() 深拷贝）
            image_copy, color_space = self.device.grab_one_frame_and_convert(
                timeout_ms=timeout_ms
            )

            cn_tz = timezone(timedelta(hours=8))
            captured_at = datetime.now(cn_tz)
            self._frame_count += 1

            # 格式化生成图片编号: <serial_number>_<带毫秒时间戳>_<帧序号>
            ts_str = captured_at.strftime("%Y%m%d%H%M%S%f")[:-3]
            image_id = f"{self.config.serial_number}_{ts_str}_{self._frame_count:06d}"

            # 相机参数与元数据提取
            camera_parameters = {
                "exposure_us": getattr(self.config, "exposure_us", 1200.0),
                "discard_frames": getattr(self.config, "discard_frames", 5),
            }

            metadata = {
                "color_space": color_space,
                "shape": list(image_copy.shape),
                "dtype": str(image_copy.dtype),
                "frame_index": self._frame_count,
                "legend": getattr(self.product, "legend", None),
                "size_u": getattr(self.product, "size_u", None),
            }

            return ImageInput(
                image=image_copy,
                image_id=image_id,
                product_id=getattr(
                    self.product, "product_id", getattr(self.product, "id", None)
                ),
                batch_id=self.batch_id,
                captured_at=captured_at,
                source_type="camera",
                source_path=None,
                camera_serial=self.config.serial_number,
                camera_parameters=camera_parameters,
                metadata=metadata,
            )

        except CameraError as err:
            raise CameraReadError(
                f"相机 [SN: {self.config.serial_number}] 读取帧失败: {err}"
            ) from err
        except Exception as err:
            raise CameraReadError(
                f"相机 [SN: {self.config.serial_number}] 读取发生异常: {err}"
            ) from err

    def __enter__(self) -> None:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
