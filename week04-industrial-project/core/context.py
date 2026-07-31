from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config_models import ModeName, RuntimeConfig
from .exceptions import InitializationError
from .paths import resolve_project_path


@dataclass(frozen=True, slots=True)
class RunContext:
    """运行上下文"""

    run_id: str
    started_at: datetime
    mode: ModeName
    output_dir: Path
    report_dir: Path


def create_run_context(config: RuntimeConfig) -> RunContext:
    """创建运行上下文"""

    try:
        cn_tz = timezone(timedelta(hours=8))
        datetime_now = datetime.now(cn_tz)
        started_at = datetime_now.astimezone()
        current_datetime_ms = datetime_now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        current_mode = config.mode_config.mode
        run_id = f"{current_datetime_ms}_{config.main_config.active_mode}"
        outputs_dir = resolve_project_path(
            config.main_config.output.outputs_dir / run_id
        )
        reports_dir = resolve_project_path(
            config.main_config.output.reports_dir / run_id
        )
        outputs_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        raise InitializationError("获取程序上下文失败") from exc
    return RunContext(
        run_id=run_id,
        started_at=started_at,
        mode=current_mode,
        output_dir=outputs_dir,
        report_dir=reports_dir,
    )
