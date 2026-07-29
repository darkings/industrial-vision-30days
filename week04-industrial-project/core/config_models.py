from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

ModeName = Literal["traditional", "yolo", "ocr", "combined"]
InputSource = Literal["camera", "image", "directory"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class StrictConfigModel(BaseModel):
    """基础严格配置模型，禁止传入未定义的额外字段"""

    model_config = ConfigDict(extra="forbid")


class AppConfig(StrictConfigModel):
    """应用程序基础信息配置"""

    name: str = Field(description="应用程序名称")
    version: str = Field(description="应用程序当前版本号")


class InputConfig(StrictConfigModel):
    """输入源配置，定义系统从何处获取图像数据"""

    source: InputSource = Field(
        description="输入源类型，可选：工业相机、单张图片或图片目录"
    )
    image_path: Path | None = Field(
        default=None, description="单张图片的路径（当 source 为 'image' 时生效）"
    )
    directory_path: Path | None = Field(
        default=None, description="图片目录的路径（当 source 为 'directory' 时生效）"
    )
    catalog_path: Path = Field(description="键帽分类方案路径")
    product_id: str | None = Field(default=None, description="键帽标识")
    batch_id: str = Field(description="产品批次")
    allowed_extensions: list[str] = Field(..., description="支持的图片格式")

    @model_validator(mode="after")
    def validate_paths_based_on_source(self) -> "InputConfig":
        """根据source的值来校验对应的路径是否提供"""

        if self.source == "image" and not all(
            [self.image_path, self.product_id, self.batch_id]
        ):
            raise ValueError(
                "当来源为单张图片时，必须提供有效的图片路径、产品标识、产品批次"
            )
        if self.source == "camera" and not all([self.product_id, self.batch_id]):
            raise ValueError("当来源为相机采集时，必须提供有效的产品标识、产品批次")
        if self.source == "directory" and not all([self.directory_path, self.batch_id]):
            raise ValueError("当来源为文件目录时，必须提供有效的文件目录路径、产品批次")
        if not self.catalog_path:
            raise ValueError("分类文件路径不能为空")
        if not self.allowed_extensions:
            raise ValueError("支持的图片格式不能为空")
        if not all(s.startswith(".") for s in self.allowed_extensions):
            raise ValueError("支持的图片格式必须以.开头")
        if len(self.allowed_extensions) != len(set(self.allowed_extensions)):
            raise ValueError("支持的图片格式不能有重复")
        return self

    @field_validator("allowed_extensions")
    @classmethod
    def low_allowed_extensions(cls, v):
        return [i.lower() for i in v]


class CameraConfig(StrictConfigModel):
    """工业相机硬件参数配置"""

    serial_number: str = Field(description="相机的唯一序列号 (SN码)")
    exposure_us: int = Field(gt=0, description="相机曝光时间（单位：微秒）")
    discard_frames: int = Field(ge=0, description="初始化时丢弃的预热帧数量")
    retry_count: int = Field(ge=0, description="相机连接或抓图失败时的重试次数")


class OutputConfig(StrictConfigModel):
    """输出管理配置，控制检测结果、图片和报告的保存逻辑"""

    outputs_dir: Path = Field(description="所有输出文件的根目录")
    reports_dir: Path = Field(description="检测报告的保存子目录")
    save_original: bool = Field(description="是否保存相机抓取的原始无损图像")
    save_annotated: bool = Field(
        description="是否保存渲染了检测框、文本等标注信息的图像"
    )
    save_debug_images: bool = Field(description="是否保存算法处理过程中的中间结果图像")


class LoggingConfig(StrictConfigModel):
    """系统日志配置"""

    level: LogLevel = Field(description="日志记录的最低级别")
    directory: Path = Field(description="日志文件的保存目录")
    console: bool = Field(description="是否在控制台终端同步输出日志")
    file_enabled: bool = Field(default=True, description="是否开启文件日志")
    max_bytes: int = Field(gt=0, description="单个日志文件的最大字节数")
    backup_count: int = Field(ge=0, description="保留的历史轮转日志文件的最大数量")


class ModeConfigPaths(StrictConfigModel):
    """各检测模式的具体算法配置文件路径"""

    traditional: Path = Field(description="传统机器视觉的配置文件路径")
    yolo: Path = Field(description="YOLO 深度学习目标检测模型的配置文件路径")
    ocr: Path = Field(description="光学字符识别 (OCR) 模型的配置文件路径")
    combined: Path = Field(description="组合流水线（多模型串联/并联）的配置文件路径")


class MainConfig(StrictConfigModel):
    """视觉检测系统的主配置入口"""

    app: AppConfig = Field(description="应用程序全局基础信息")
    active_mode: ModeName = Field(description="当前激活的检测模式")
    mode_configs: ModeConfigPaths = Field(
        description="各检测模式所对应的子配置文件路径清单"
    )
    input: InputConfig = Field(description="输入数据源设置")
    camera: CameraConfig = Field(description="相机硬件与抓图参数设置")
    output: OutputConfig = Field(description="文件与数据输出路径设置")
    logging: LoggingConfig = Field(description="系统运行日志设置")


class TraditionalProcessingConfig(StrictConfigModel):
    """传统图像预处理相关配置项。"""

    threshold_method: Literal["otsu", "fixed"] = Field(
        ..., description="二值化阈值方法 (otsu/fixed)"
    )
    fixed_threshold: int | None = Field(
        default=None,
        ge=0,
        le=255,
        description="固定阈值，仅在 threshold_method='fixed' 时生效",
    )
    blur_kernel: int = Field(..., gt=0, description="模糊核大小 (必须为正奇数)")
    morphology_kernel: int = Field(..., gt=0, description="形态学核大小 (必须为正奇数)")

    @field_validator("blur_kernel", "morphology_kernel")
    @classmethod
    def validate_odd(cls, v: int) -> int:
        """校验卷积核尺寸是否为正奇数。"""
        if v % 2 == 0:
            raise ValueError("卷积核尺寸必须是正奇数")
        return v

    @model_validator(mode="after")
    def validate_threshold_logic(self) -> "TraditionalProcessingConfig":
        """校验当二值化模式为 fixed 时，固定阈值参数不能为空。"""
        if self.threshold_method == "fixed" and self.fixed_threshold is None:
            raise ValueError("当二值化类型为fixed时，阈值不能为空")
        return self


class SizeRuleConfig(StrictConfigModel):
    """目标尺寸与纵横比范围过滤规则配置。"""

    min_area: float | None = Field(default=None, gt=0, description="最小像素面积")
    max_area: float | None = Field(default=None, gt=0, description="最大像素面积")
    min_aspect_ratio: float | None = Field(default=None, gt=0, description="最小纵横比")
    max_aspect_ratio: float | None = Field(default=None, gt=0, description="最大纵横比")

    @model_validator(mode="after")
    def validate_area_range(self) -> "SizeRuleConfig":
        """校验面积及纵横比的最小值是否小于或等于最大值。"""
        if (
            self.min_area is not None
            and self.max_area is not None
            and self.min_area > self.max_area
        ):
            raise ValueError("最大区域和最小区域都存在时，最小区域不能大于最大区域")

        if (
            self.min_aspect_ratio is not None
            and self.max_aspect_ratio is not None
            and self.min_aspect_ratio > self.max_aspect_ratio
        ):
            raise ValueError(
                "最大 纵横比和最小纵横比都存在时，最小纵横比不能大于最大纵横比"
            )
        return self


class TraditionalRulesConfig(StrictConfigModel):
    """传统图像处理判定规则配置。"""

    expected_count: int = Field(..., ge=0, description="期望检测到的目标数量")
    center_tolerance_px: int = Field(..., ge=0, description="中心点容忍误差(像素)")
    size_profiles: dict[str, SizeRuleConfig] = Field(
        ..., description="尺寸规则配置字典"
    )


class TraditionalConfig(StrictConfigModel):
    """传统图像处理完整模式配置。"""

    mode: Literal["traditional"] = Field(..., description="配置模式标识")
    config_version: str = Field(..., description="配置版本")
    profile: Literal["single_keycap"] = Field(..., description="业务配置类型")
    processing: TraditionalProcessingConfig = Field(..., description="图像预处理配置")
    rules: TraditionalRulesConfig = Field(..., description="检测规则配置")


class YoloModelConfig(StrictConfigModel):
    """YOLO 模型推理引擎与输入配置。"""

    path: Path = Field(..., description="模型文件路径")
    version: str = Field(..., description="模型版本")
    confidence: float = Field(..., ge=0, le=1, description="置信度阈值 (0-1)")
    iou: float = Field(..., ge=0, le=1, description="IOU 阈值 (0-1)")
    image_size: int = Field(..., gt=0, description="输入图像尺寸")
    device: str = Field(..., description="推理设备 (如 cpu, cuda:0)")


class YoloRulesConfig(StrictConfigModel):
    """YOLO 目标检测校验规则配置。"""

    expected_class: Literal["keycap"] = Field(..., description="期望检测的目标类别")
    expected_count: int = Field(..., ge=0, description="期望检测到的目标数量")
    reject_duplicate_boxes: bool = Field(..., description="是否拒绝重复框")


class YoloConfig(StrictConfigModel):
    """YOLO 检测模式完整配置。"""

    mode: Literal["yolo"] = Field(..., description="配置模式标识")
    config_version: str = Field(..., description="配置版本")
    model: YoloModelConfig = Field(..., description="YOLO 模型配置")
    rules: YoloRulesConfig = Field(..., description="YOLO 规则配置")


class OcrModelConfig(StrictConfigModel):
    """OCR 识别模型配置。"""

    lang: str = Field(..., description="OCR 语言类型")
    use_textline_orientation: bool = Field(..., description="是否使用文本行方向判断")
    enable_mkldnn: bool = Field(..., description="是否启用 MKLDNN 加速")


class OcrPreprocessConfig(StrictConfigModel):
    """OCR 专用图像预处理配置。"""

    grayscale: bool = Field(..., description="是否进行灰度化")
    threshold_method: Literal["none", "otsu", "fixed"] = Field(
        ..., description="二值化处理方式"
    )
    fixed_threshold: int | None = Field(
        default=None, ge=0, le=255, description="固定二值化阈值"
    )
    scale: float = Field(..., gt=0, description="图像缩放比例")

    @model_validator(mode="after")
    def validate_threshold_logic(self) -> "OcrPreprocessConfig":
        """校验当二值化模式为 fixed 时，固定阈值参数不能为空。"""
        if self.threshold_method == "fixed" and self.fixed_threshold is None:
            raise ValueError("当二值化的方法为fixed时，阈值不能为空")
        return self


class OcrRulesConfig(StrictConfigModel):
    """OCR 文字识别判定规则配置。"""

    min_confidence: float = Field(..., ge=0, le=1, description="识别最小置信度 (0-1)")
    expected_legend: str | None = Field(default=None, description="期望识别的字符文本")
    allow_empty_result: bool = Field(..., description="是否允许识别结果为空")


class OcrConfig(StrictConfigModel):
    """OCR 文字识别模式完整配置。"""

    mode: Literal["ocr"] = Field(..., description="配置模式标识")
    config_version: str = Field(..., description="配置版本")
    model: OcrModelConfig = Field(..., description="OCR 模型配置")
    preprocess: OcrPreprocessConfig = Field(..., description="预处理配置")
    rules: OcrRulesConfig = Field(..., description="OCR 规则配置")


class CombinedComponentsConfig(StrictConfigModel):
    """多管道算法组件启用开关。"""

    traditional: bool = Field(..., description="是否开启传统算法")
    yolo: bool = Field(..., description="是否开启 YOLO 算法")
    ocr: bool = Field(..., description="是否开启 OCR 算法")

    @model_validator(mode="after")
    def has_enabled_component(self) -> "CombinedComponentsConfig":
        """校验是否至少启用了传统、YOLO 或 OCR 中的一个组件。"""
        if self.traditional is False and self.yolo is False and self.ocr is False:
            raise ValueError("请至少启用一个组件")
        return self


class CombinedRulesConfig(StrictConfigModel):
    """多管道组合结果过滤与判定规则。"""

    require_exact_count: bool = Field(..., description="是否要求数量精确匹配")
    reject_missing_legends: bool = Field(..., description="是否拒绝字符缺失")
    reject_duplicate_legends: bool = Field(..., description="是否拒绝字符重复")
    reject_unexpected_legends: bool = Field(..., description="是否拒绝未预期的字符")


class CombinedConfig(StrictConfigModel):
    """多管道算法组合模式完整配置。"""

    mode: Literal["combined"] = Field(..., description="配置模式标识")
    config_version: str = Field(..., description="配置版本")
    batch_file: Path = Field(..., description="批次配置文件路径")
    components: CombinedComponentsConfig = Field(..., description="组件开关配置")
    rules: CombinedRulesConfig = Field(..., description="组合规则配置")


class BatchConfig(StrictConfigModel):
    """批次测试任务配置文件结构。"""

    set_id: str = Field(..., description="套件编号")
    batch_id: str = Field(..., description="批次编号")
    expected_count: int = Field(..., gt=0, description="预期目标总数")
    expected_legends: list[str] = Field(..., description="预期字符字符串数组")

    @model_validator(mode="after")
    def validate_expected_legends(self) -> "BatchConfig":
        """校验预期字符列表的长度是否匹配，以及列表内字符串元素是否有效（非空）。"""
        if len(self.expected_legends) != self.expected_count:
            raise ValueError("字符列表长度必须等于期望长度")
        for i, legend in enumerate(self.expected_legends):
            if not legend.strip():
                raise ValueError(f"字符列表中，第{i + 1}个字符不能为空或空白字符")
        return self


MODE_CONFIG_MODELS: dict[str, type[StrictConfigModel]] = {
    "traditional": TraditionalConfig,
    "yolo": YoloConfig,
    "ocr": OcrConfig,
    "combined": CombinedConfig,
}


ModeConfig = TraditionalConfig | YoloConfig | OcrConfig | CombinedConfig


class RuntimeConfig(StrictConfigModel):
    main_config: MainConfig
    mode_config: ModeConfig

    @model_validator(mode="after")
    def validate_active_mode(self):
        if self.main_config.active_mode != self.mode_config.mode:
            raise ValueError("主配置激活的模式必须与当前模式一致")
        return self
