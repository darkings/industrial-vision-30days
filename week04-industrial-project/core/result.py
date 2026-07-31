from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

INSPECTION_SCHEMA_VERSION = "1.0.0"


class ExecutionStatus(str, Enum):
    """是否完成检测流程枚举"""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class InspectionResult(str, Enum):
    """产品检测结论枚举"""

    OK = "OK"
    NG = "NG"
    UNKNOWN = "UNKNOWN"


class StricResultModel(BaseModel):
    """统一结果基类"""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())


class ErrorInfo(StricResultModel):
    """程序执行异常或失败时的详细错误信息描述"""

    error_type: str = Field(
        description="错误类型，如 TimeoutError, ModelLoadError, CUDAOutOfMemory"
    )
    stage: str = Field(
        description="触发错误的业务阶段，如 preprocess, inference, postprocess"
    )
    message: str = Field(description="可读的详细错误堆栈或提示信息")
    recoverable: bool = Field(
        description="错误是否可恢复/可重试（True 代表可以自动重试或继续处理下一张）"
    )


class VersionInfo(StricResultModel):
    """算法与系统版本控制信息"""

    app_version: str = Field(description="应用程序的版本号")
    config_version: str = Field(description="配置文件版本号")
    model_version: str | None = Field(
        default=None, description="推理模型或算法资产版本号；无独立模型时为 None"
    )


class ResultPaths(StricResultModel):
    """质检过程相关的输入输出文件路径集合"""

    input_path: Path | None = Field(
        default=None, description="原始输入图像的物理存储路径"
    )
    annotated_path: Path | None = Field(
        default=None, description="带渲染标注框/缺陷框的输出图像路径"
    )
    json_path: Path | None = Field(
        default=None, description="完整质检记录保存的 JSON 文件路径"
    )


class TimingInfo(StricResultModel):
    """检测生命周期各阶段的耗时统计（单位：毫秒）"""

    preprocess_ms: float = Field(
        ge=0.0,
        description="预处理耗时（毫秒），包括图像读取、Resize、归一化等，必须 >= 0",
    )
    inference_ms: float = Field(
        ge=0.0, description="模型推理或传统算法计算耗时（毫秒），必须 >= 0"
    )
    total_ms: float = Field(
        ge=0.0, description="从请求接收到输出生成的总耗时（毫秒），必须 >= 0"
    )


class InspectionRecord(StricResultModel):
    """工业质检单次检测记录的主契约模型"""

    schema_version: str = Field(
        description="数据契约 Schema 的版本号，用于应对后续字段变更与兼容"
    )
    run_id: str = Field(description="单次服务运行或流水线批次调用的唯一标识符")
    image_id: str = Field(description="被检测图像的唯一 ID")
    batch_id: str | None = Field(default=None, description="所属生产批次号 ID，选填")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now().astimezone(),
        description="检测完成的时间戳",
    )
    mode: Literal["traditional", "yolo", "ocr", "combined"] = Field(
        description="使用的检测模式：traditional (传统视觉) | yolo (深度学习) | ocr (文本识别) | combined (混合模式)"
    )

    execution_status: ExecutionStatus = Field(
        description="程序的执行状态：SUCCESS (运行成功) | ERROR (运行异常)"
    )
    inspection_result: InspectionResult = Field(
        description="质检判定结果：OK (合格) | NG (不合格) | UNKNOWN (未知/未检出)"
    )
    reason_codes: list[str] = Field(
        description="结果判定原因/缺陷代码列表。不能为空，且不能包含空白串"
    )
    message: str = Field(description="人类可读的汇总摘要或状态说明")

    measurements: dict[str, Any] = Field(
        default_factory=dict,
        description="检测过程中的定量测量数据字典（如尺寸、面积、置信度分数等）",
    )
    versions: VersionInfo = Field(description="关联的版本元数据信息")
    paths: ResultPaths = Field(description="关联的文件路径信息")
    timing: TimingInfo = Field(description="各阶段耗时统计信息")
    error: ErrorInfo | None = Field(
        default=None, description="发生错误时的详细信息，SUCCESS 状态下必须为 None"
    )

    @model_validator(mode="after")
    def validate_inspection_logic(self) -> "InspectionRecord":
        status = self.execution_status
        result = self.inspection_result
        error = self.error
        reasons = self.reason_codes

        if not reasons:
            raise ValueError("reason_codes 不能为空列表。")
        if any(not rc.strip() for rc in reasons):
            raise ValueError("reason_codes 中不能包含空字符串或纯空白字符串。")

        if status == ExecutionStatus.ERROR and result in (
            InspectionResult.OK,
            InspectionResult.NG,
        ):
            raise ValueError(f"执行状态为 ERROR 时，检测结果不能是 {result.value}。")

        if (
            status == ExecutionStatus.ERROR
            and result == InspectionResult.UNKNOWN
            and error is None
        ):
            raise ValueError(
                "执行状态为 ERROR 且结果为 UNKNOWN 时，error 字段不能为空。"
            )

        if status == ExecutionStatus.SUCCESS and error is not None:
            raise ValueError("执行状态为 SUCCESS 时，error 字段必须为 None。")

        return self
