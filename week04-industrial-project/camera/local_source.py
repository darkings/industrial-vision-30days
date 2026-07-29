from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.catalog import KeycapProduct
from core.exceptions import ImageReadError
from core.paths import resolve_project_path

from camera.image_source import ImageInput, ImageSource


class LocalImageSource(ImageSource):
    def __init__(
        self,
        image_path: Path,
        product: KeycapProduct,
        batch_id: str,
        allowed_extensions: list[str],
    ):
        self.image_path = image_path
        self.product = product
        self.batch_id = batch_id
        self.allowed_extensions = allowed_extensions
        self._opened = False
        self._has_read = False
        self._closed = False

    def open(self):
        image_path = resolve_project_path(self.image_path)
        if not image_path.exists():
            raise ImageReadError(
                image_path, message=f"无法读取图片: 当前路径不存在 {image_path}"
            )
        if not image_path.is_file():
            raise ImageReadError(
                image_path, message=f"无法读取图片: 当前路径不是一个文件 {image_path}"
            )
        if image_path.suffix.lower() not in self.allowed_extensions:
            raise ImageReadError(
                image_path, message=f"无法读取图片: 图片格式不支持 {image_path.suffix}"
            )
        self.image_path = image_path
        self._opened = True
        self._closed = False
        self._has_read = False

    def read(self):
        if not self._opened:
            raise ImageReadError(self.image_path, message="请先调用open")
        if not self._has_read:
            import cv2

            image = cv2.imread(str(self.image_path))
            mtime = self.image_path.stat().st_mtime
            cn_tz = timezone(timedelta(hours=8))
            captured_at = datetime.fromtimestamp(mtime, tz=cn_tz)
            if image is None:
                raise ImageReadError(self.image_path)
            metadata = {
                "timestamp_source": "file_mtime",
                "file_mtime": mtime,
                "color_space": "BGR",
                "shape": list(image.shape),
                "dtype": str(image.dtype),
                "legend": self.product.legend,
                "size_u": self.product.size_u,
            }
            self._has_read = True
            return ImageInput(
                image=image,
                image_id=self.image_path.stem,
                product_id=self.product.product_id,
                batch_id=self.batch_id,
                captured_at=captured_at,
                source_type="image",
                source_path=self.image_path,
                metadata=metadata,
            )

        else:
            return None

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._opened = False
