import copy
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core import (
    BatchConfig,
    CombinedConfig,
    OcrConfig,
    TraditionalConfig,
    YoloConfig,
)


def test_01(
    traditional_config_dict,
    yolo_config_dict,
    ocr_config_dict,
    combined_config_dict,
    batch_config_dict,
):
    """正确配置：创建并验证"""

    traditional_config = TraditionalConfig.model_validate(traditional_config_dict)
    yolo_config = YoloConfig.model_validate(yolo_config_dict)
    ocr_config = OcrConfig.model_validate(ocr_config_dict)
    combined_config = CombinedConfig.model_validate(combined_config_dict)
    batch_config = BatchConfig.model_validate(batch_config_dict)

    print(type(traditional_config).__name__)
    print(traditional_config.mode)
    print(traditional_config.config_version)
    print(traditional_config.model_dump_json(indent=4))
    print(type(yolo_config).__name__)
    print(yolo_config.mode)
    print(yolo_config.config_version)
    print(yolo_config.model_dump_json(indent=4))
    print(type(ocr_config).__name__)
    print(ocr_config.mode)
    print(ocr_config.config_version)
    print(ocr_config.model_dump_json(indent=4))
    print(type(combined_config).__name__)
    print(combined_config.mode)
    print(combined_config.config_version)
    print(combined_config.model_dump_json(indent=4))
    print(type(batch_config).__name__)
    print(batch_config.batch_id)
    print(batch_config.set_id)
    print(batch_config.model_dump_json(indent=4))


def test_02(traditional_config_dict):
    """错误验证：正奇数验证失败"""
    try:
        invalid_data = copy.deepcopy(traditional_config_dict)
        invalid_data["processing"]["blur_kernel"] = 4

        TraditionalConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期奇数验证失败，但验证成功")


def test_03(traditional_config_dict):
    """错误验证：范围关系验证失败"""
    try:
        invalid_data = copy.deepcopy(traditional_config_dict)
        invalid_data["rules"]["size_profiles"]["standard_keycap"]["min_area"] = 200
        invalid_data["rules"]["size_profiles"]["standard_keycap"]["max_area"] = 100
        TraditionalConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期范围关系验证失败，但验证成功")


def test_04(yolo_config_dict):
    """错误验证：0–1范围验证失败"""
    try:
        invalid_data = copy.deepcopy(yolo_config_dict)
        invalid_data["model"]["confidence"] = 1.5

        YoloConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期0–1范围验证失败，但验证成功")


def test_05(ocr_config_dict):
    """错误验证：交叉验证失败"""
    try:
        invalid_data = copy.deepcopy(ocr_config_dict)
        invalid_data["preprocess"]["threshold_method"] = "fixed"
        invalid_data["preprocess"]["fixed_threshold"] = None

        OcrConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期交叉验证失败，但验证成功")


def test_06(combined_config_dict):
    """错误验证：至少启用一个组件验证失败"""
    try:
        invalid_data = copy.deepcopy(combined_config_dict)
        invalid_data["components"]["traditional"] = False
        invalid_data["components"]["yolo"] = False
        invalid_data["components"]["ocr"] = False

        CombinedConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期至少启用一个组件验证失败，但验证成功")


def test_07(batch_config_dict):
    """错误验证：数量关系验证失败"""
    try:
        invalid_data = copy.deepcopy(batch_config_dict)
        invalid_data["expected_count"] = 8
        invalid_data["expected_legends"] = ["1", "2", "3", "4", "5", "6", "7"]

        BatchConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期数量关系验证失败，但验证成功")


def test_08(yolo_config_dict):
    """错误验证：Literal验证失败"""
    try:
        invalid_data = copy.deepcopy(yolo_config_dict)
        invalid_data["mode"] = "traditional"

        YoloConfig.model_validate(invalid_data)
    except ValidationError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期Literal验证失败，但验证成功")


def main():
    traditional_config_dict = {
        "mode": "traditional",
        "config_version": "1.0.0",
        "profile": "single_keycap",
        "processing": {
            "threshold_method": "fixed",
            "fixed_threshold": 128,
            "blur_kernel": 3,
            "morphology_kernel": 5,
        },
        "rules": {
            "expected_count": 1,
            "center_tolerance_px": 10,
            "size_profiles": {
                "standard_keycap": {
                    "min_area": 1000.0,
                    "max_area": 5000.0,
                    "min_aspect_ratio": 0.8,
                    "max_aspect_ratio": 1.2,
                }
            },
        },
    }

    yolo_config_dict = {
        "mode": "yolo",
        "config_version": "1.0.0",
        "model": {
            "path": "models/yolo/keycap_v1.pt",
            "version": "v8n",
            "confidence": 0.85,
            "iou": 0.45,
            "image_size": 640,
            "device": "cuda:0",
        },
        "rules": {
            "expected_class": "keycap",
            "expected_count": 1,
            "reject_duplicate_boxes": True,
        },
    }

    ocr_config_dict = {
        "mode": "ocr",
        "config_version": "1.0.0",
        "model": {
            "lang": "en",
            "use_textline_orientation": True,
            "enable_mkldnn": True,
        },
        "preprocess": {
            "grayscale": True,
            "threshold_method": "otsu",
            "fixed_threshold": None,
            "scale": 1.5,
        },
        "rules": {
            "min_confidence": 0.90,
            "expected_legend": "A",
            "allow_empty_result": False,
        },
    }

    combined_config_dict = {
        "mode": "combined",
        "config_version": "1.0.0",
        "batch_file": "data/batches/BATCH_01.yaml",
        "components": {
            "traditional": True,
            "yolo": True,
            "ocr": True,
        },
        "rules": {
            "require_exact_count": True,
            "reject_missing_legends": True,
            "reject_duplicate_legends": True,
            "reject_unexpected_legends": True,
        },
    }

    batch_config_dict = {
        "set_id": "SET_001",
        "batch_id": "BATCH_01",
        "expected_count": 8,
        "expected_legends": ["ESC", "1", "2", "3", "4", "5", "6", "7"],
    }

    test_01(
        traditional_config_dict,
        yolo_config_dict,
        ocr_config_dict,
        combined_config_dict,
        batch_config_dict,
    )
    test_02(traditional_config_dict)
    test_03(traditional_config_dict)
    test_04(yolo_config_dict)
    test_05(ocr_config_dict)
    test_06(combined_config_dict)
    test_07(batch_config_dict)
    test_08(yolo_config_dict)


if __name__ == "__main__":
    main()
