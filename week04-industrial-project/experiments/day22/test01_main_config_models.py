import copy
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.config_models import MainConfig


def test_01(data):
    """测试1：正确配置"""
    valid_data = copy.deepcopy(data)
    config = MainConfig.model_validate(valid_data)
    assert isinstance(config.mode_configs.traditional, Path)
    print(config.active_mode)
    print(config.input.source)
    print(config.camera.exposure_us)
    print(config.mode_configs.traditional)
    print(config.model_dump_json(indent=4))


def test_02(data):
    """测试2：未知字段"""
    valid_data = copy.deepcopy(data)
    valid_data["camera"]["exposuer_us"] = valid_data["camera"].pop("exposure_us")
    try:
        MainConfig.model_validate(valid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期ValidationError，但验证成功")


def test_03(data):
    """测试3：错误模式"""
    valid_data = copy.deepcopy(data)
    valid_data["active_mode"] = "traditonal"
    try:
        MainConfig.model_validate(valid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期ValidationError，但验证成功")


def test_04(data):
    """测试4：输入源缺少路径"""
    valid_data = copy.deepcopy(data)
    valid_data["input"]["source"] = "image"
    valid_data["input"]["image_path"] = None
    try:
        MainConfig.model_validate(valid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期ValidationError，但验证成功")


def main():
    valid_data = {
        "app": {
            "name": "Multi-Mode Keycap Vision Inspection System",
            "version": "1.0.0",
        },
        "active_mode": "combined",  # 可选: "traditional", "yolo", "ocr", "combined"
        "mode_configs": {
            "traditional": "configs/modes/traditional.yaml",
            "yolo": "configs/modes/yolo.yaml",
            "ocr": "configs/modes/ocr.yaml",
            "combined": "configs/modes/combined.yaml",
        },
        "input": {
            "source": "camera",
            "image_path": None,
            "directory_path": None,
        },
        "camera": {
            "serial_number": "SN123456789",
            "exposure_us": 5000,
            "discard_frames": 2,
            "retry_count": 3,
        },
        "output": {
            "outputs_dir": "outputs/",
            "reports_dir": "reports/",
            "save_original": True,
            "save_annotated": True,
            "save_debug_images": False,
        },
        "logging": {
            "level": "INFO",
            "directory": "logs/",
            "console": True,
            "max_bytes": 10485760,
            "backup_count": 5,
        },
    }

    test_01(valid_data)
    test_02(valid_data)
    test_03(valid_data)
    test_04(valid_data)


if __name__ == "__main__":
    main()
