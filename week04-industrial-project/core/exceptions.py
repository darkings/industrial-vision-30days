from pathlib import Path

from .exit_codes import ExitCode


class InspectionError(Exception):
    """所有可映射为退出码的业务异常基类"""

    # 使用未知异常兜底
    exit_code: ExitCode = ExitCode.UNEXPECTED_ERROR

    @property
    def error_code(self) -> int:
        """返回错误码"""
        return int(self.exit_code)

    def __str__(self) -> str:
        """将异常转成字符串"""

        text = super().__str__()
        return text if text else self.__class__.__name__

    def log_message(self) -> str:
        """生成适合logger 输出的日志信息"""

        return f"错误码[{self.exit_code}] {self}"


class ConfigError(InspectionError):
    """配置加载失败，或者配置内容不合法。"""

    exit_code: ExitCode = ExitCode.CONFIG_ERROR


class InitializationError(InspectionError):
    """应用初始化失败。"""

    exit_code: ExitCode = ExitCode.INITIALIZATION_ERROR


class CatalogError(InspectionError):
    """目录 / 类别相关异常基类。"""

    exit_code: ExitCode = ExitCode.CATALOG_ERROR


class ProductNotFoundError(CatalogError):
    """产品未找到异常"""

    exit_code: ExitCode = ExitCode.PRODUCT_NOT_FOUND

    def __init__(self, product_id: str, message: str | None = None):
        # 保存业务上下文，方便日志直接定位到具体产品
        self.product_id = product_id
        super().__init__(message or f"无法寻找到标识为 {product_id} 的产品")


class FeatureNotImplementedError(InspectionError):
    """功能已预留，但尚未实现。"""

    exit_code: ExitCode = ExitCode.FEATURE_NOT_IMPLEMENTED


class UnexpectedError(InspectionError):
    """未知异常包装类,作为兜底使用"""

    exit_code: ExitCode = ExitCode.UNEXPECTED_ERROR


class InputSourceError(InspectionError):
    """输入源基础异常"""

    exit_code: ExitCode = ExitCode.INPUT_ERROR


class SourceNotOpenedError(InitializationError):
    """输入源未打开异常"""

    exit_code: ExitCode = ExitCode.INITIALIZATION_ERROR

    def __init__(self, source: str | int | None = None, message: str | None = None):
        self.source = source

        if source is None:
            super().__init__(message or "请先调用 open() 后再读取图像")
        else:
            super().__init__(
                message or f"输入源[{source}]尚未打开，请先调用 open() 后再读取图像"
            )


class ImageReadError(InputSourceError):
    """图片读取基础异常"""

    exit_code: ExitCode = ExitCode.INPUT_ERROR

    def __init__(self, path: str, message: str | None = None):
        self.path = path
        super().__init__(message or f"无法读取图片: {path}")


class ImageNotFoundError(ImageReadError):
    """图片文件不存在。"""

    exit_code: ExitCode = ExitCode.IMAGE_NOT_FOUND

    def __init__(self, path: str, message: str | None = None):
        super().__init__(path, message or f"图片文件不存在: {path}")


class InputNotFileError(ImageReadError):
    """输入路径不是一个有效文件。"""

    exit_code: ExitCode = ExitCode.INPUT_NOT_FILE

    def __init__(self, path: str, message: str | None = None):
        super().__init__(path, message or f"输入不是文件: {path}")


class UnsupportedImageFormatError(ImageReadError):
    """图片格式不支持。"""

    exit_code: ExitCode = ExitCode.UNSUPPORTED_IMAGE_FORMAT

    def __init__(self, path: str, message: str | None = None):
        # 直接复用父类的 path 保存逻辑
        super().__init__(path, message or f"不支持的图片格式: {Path(path).suffix}")


class ImageDecodeError(ImageReadError):
    """图片解码失败。"""

    exit_code: ExitCode = ExitCode.IMAGE_DECODE_ERROR

    def __init__(self, path: str, message: str | None = None):
        super().__init__(path, message or f"图片解码失败: {path}")


class NoImageAvailableError(InputSourceError):
    """当前没有可用图像"""

    exit_code: ExitCode = ExitCode.NO_IMAGE_AVAILABLE

    def __init__(self, source: str | None = None, message: str | None = None):
        self.source = source
        if source:
            super().__init__(message or f"当前没有可用图像: {source}")
        else:
            super().__init__(message or "当前没有可用图像")


class CameraError(InputSourceError):
    """相机相关异常基础类"""

    exit_code: ExitCode = ExitCode.INPUT_ERROR

    def __init__(self, index: int | str, message: str | None = None):
        self.index = index
        super().__init__(message or f"相机异常: {index}")


class CameraOpenError(CameraError):
    """相机打开异常。"""

    exit_code: ExitCode = ExitCode.INITIALIZATION_ERROR

    def __init__(self, index: int | str, message: str | None = None):
        super().__init__(index, message or f"无法打开相机: {index}")


class CameraReadError(CameraError):
    """相机读取异常。"""

    exit_code: ExitCode = ExitCode.INPUT_ERROR

    def __init__(self, index: int | str, message: str | None = None):
        super().__init__(index, message or f"无法从相机读取图片: {index}")


class SizeProfileNotFoundError(ConfigError):
    """未找到对应尺寸的 profile。"""

    exit_code: ExitCode = ExitCode.CONFIG_ERROR

    def __init__(self, size_u: float, message: str | None = None):
        self.size_u = size_u
        super().__init__(message or f"未找到尺寸 {size_u:.1f}u 对应的 profile")


class ModeConfigTypeError(ConfigError):
    """mode_config 的类型与预期不一致。"""

    # 仍然归类为配置错误，因此退出码保持 10
    exit_code: ExitCode = ExitCode.CONFIG_ERROR
