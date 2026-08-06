from datetime import datetime, timedelta, timezone
from logging import LoggerAdapter
from pathlib import Path

from core import (
    ExecutionStatus,
    InspectionRecord,
    InspectionResult,
    ModeName,
    RunContext,
    StricResultModel,
)

from .json_writer import write_json

RUN_SUMMARY_VERSION = "1.0.0"


class RunSummary(StricResultModel):
    """运行摘要数据模型"""

    schema_version: str
    run_id: str
    mode: ModeName
    started_at: datetime
    finished_at: datetime
    total_count: int
    success_count: int
    error_count: int
    ok_count: int
    ng_count: int
    unknown_count: int
    reason_code_counts: dict[str, int]
    average_total_ms: float
    max_total_ms: float
    ok_image_ids: list[str]
    ng_image_ids: list[str]
    error_image_ids: list[str]
    record_paths: list[Path]


class SummaryWriter:
    def __init__(self, context: RunContext, logger: LoggerAdapter):
        """初始化摘要写入器，使用指定的输出配置"""

        self.context = context
        self.logger = logger

    def write(self, records: list[InspectionRecord]) -> RunSummary:
        """将检测记录列表写入摘要"""

        summary = RunSummary(
            schema_version=RUN_SUMMARY_VERSION,
            run_id=self.context.run_id,
            mode=self.context.mode,
            started_at=self.context.started_at,
            finished_at=datetime.now(timezone(timedelta(hours=8))),
            total_count=len(records),
            success_count=0,
            error_count=0,
            ok_count=0,
            ng_count=0,
            unknown_count=0,
            reason_code_counts={},
            average_total_ms=0,
            max_total_ms=0,
            ok_image_ids=[],
            ng_image_ids=[],
            error_image_ids=[],
            record_paths=[],
        )
        summary.success_count = sum(
            record.execution_status == ExecutionStatus.SUCCESS for record in records
        )
        summary.error_count = sum(
            record.execution_status == ExecutionStatus.ERROR for record in records
        )
        summary.ok_count = sum(
            record.inspection_result == InspectionResult.OK for record in records
        )
        summary.ng_count = sum(
            record.inspection_result == InspectionResult.NG for record in records
        )
        summary.unknown_count = sum(
            record.inspection_result == InspectionResult.UNKNOWN for record in records
        )
        summary.ok_image_ids = [
            record.image_id
            for record in records
            if record.inspection_result == InspectionResult.OK
        ]
        summary.ng_image_ids = [
            record.image_id
            for record in records
            if record.inspection_result == InspectionResult.NG
        ]
        summary.error_image_ids = [
            record.image_id
            for record in records
            if record.execution_status == ExecutionStatus.ERROR
        ]
        summary.record_paths = [
            record.paths.json_path
            for record in records
            if record.paths.json_path is not None
        ]
        total_times = [record.timing.total_ms for record in records]
        summary.max_total_ms = max(total_times, default=0)
        summary.average_total_ms = (
            sum(total_times) / len(total_times) if total_times else 0
        )
        summary.reason_code_counts = {
            reason_code: sum(reason_code in record.reason_codes for record in records)
            for reason_code in {
                reason_code for record in records for reason_code in record.reason_codes
            }
        }
        summary_path = self.context.report_dir / "summary.json"
        saved_path = write_json(summary_path, summary)
        self.logger.info("运行摘要保存成功 | path=%s", saved_path)
        return summary
