class InputSourceError(Exception):
    """输入源基础异常"""


class ImageReadError(InputSourceError):
    """图片读取异常"""

    def __init__(self, path: str, message: str | None = None):
        self.path = path
        super().__init__(message or f"无法读取图片: {path}")


class CameraOpenError(InputSourceError):
    """相机打开异常"""

    def __init__(self, index: int | str, message: str | None = None):
        self.index = index
        super().__init__(message or f"无法打开相机:{index}")


class CameraReadError(InputSourceError):
    """相机读取异常"""

    def __init__(self, index: int | str, message: str | None = None):
        self.index = index
        super().__init__(message or f"无法从相机读取图片:{index}")


class CatalogError(Exception):
    """类别异常基类"""


class ProductNotFoundError(CatalogError):
    """产品寻找不到异常"""

    def __init__(self, product_id: str, message: str | None = None):
        self.product_id = product_id
        super().__init__(message or f"无法寻找到标识为{product_id}的产品")
