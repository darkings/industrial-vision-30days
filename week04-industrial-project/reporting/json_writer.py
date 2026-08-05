from pathlib import Path

from core import InspectionRecord, JsonWriteError


def write_json(path: Path, records: InspectionRecord):
    """写入JSON"""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(records.model_dump_json(indent=2), encoding="utf-8")
        return path
    except (OSError, TypeError, ValueError) as exc:
        raise JsonWriteError(path, message=f"写入JSON失败 路径：{path} 错误：{exc}")
