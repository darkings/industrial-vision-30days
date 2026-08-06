from enum import IntEnum


class ExitCode(IntEnum):
    """
    应用统一退出码。

    约定：
    * 0 表示成功
    * 10~19 表示配置/初始化错误
    * 20~29 表示目录/产品相关错误
    * 30~39 表示输入源/图像相关错误
    * 40~49 表示功能未实现
    * 50~59 表示输出保存错误
    * 99 表示未知异常
    """

    SUCCESS = 0  # 程序正常执行完成

    # 配置 / 初始化类错误
    CONFIG_ERROR = 10  # 配置加载失败，或配置内容不合法
    INITIALIZATION_ERROR = 11  # 应用初始化失败，例如依赖对象创建失败

    # 目录 / 产品类错误
    CATALOG_ERROR = 20  # 键帽目录加载失败，或目录数据异常
    PRODUCT_NOT_FOUND = 21  # 根据条件未找到对应产品

    # 输入源 / 图像类错误
    INPUT_ERROR = 30  # 输入源通用错误
    IMAGE_NOT_FOUND = 31  # 输入源中没有获取到图像
    INPUT_NOT_FILE = 32  # 输入不是有效文件
    UNSUPPORTED_IMAGE_FORMAT = 33  # 图像格式不支持
    IMAGE_DECODE_ERROR = 34  # 图像解码失败
    NO_IMAGE_AVAILABLE = 35  # 当前没有可用图像，例如队列为空或摄像头无帧
    IMAGE_DIRECTORY_NOT_FOUND = 36  # 图片目录不存在

    # 输出保存类错误
    OUTPUT_ERROR = 50
    IMAGE_WRITE_ERROR = 51
    JSON_WRITE_ERROR = 52

    PIPELINE_ERROR = 60  # 流水线执行失败，例如模型推理失败或后处理异常

    # 功能未实现
    FEATURE_NOT_IMPLEMENTED = 40  # 代码逻辑已预留，但功能尚未实现

    # 未知异常
    UNEXPECTED_ERROR = 99  # 未捕获的未知错误
