from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).resolve().parents[1]


def resolve_project_path(path: str | Path) -> Path:
    """解析项目路径"""

    path = Path(path)

    if path.is_absolute():
        return path

    return PROJECT_ROOT_PATH / path
