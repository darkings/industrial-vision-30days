# -- coding: utf-8 --
"""
Day 8：曝光对比实验中的图像统计函数测试。

这个测试不连接相机，只验证统计函数本身是否正确。
"""

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parent / "test04_hik_exposure_comparison.py"


def load_exposure_module():
    spec = importlib.util.spec_from_file_location("test04_hik_exposure_comparison", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_calculate_image_stats_counts_saturated_pixels():
    module = load_exposure_module()

    image = np.array(
        [
            [0, 128, 255],
            [255, 64, 32],
        ],
        dtype=np.uint8,
    )

    stats = module.calculate_image_stats(image)

    assert stats["width"] == 3
    assert stats["height"] == 2
    assert stats["mean_gray"] == 122.33
    assert stats["min_gray"] == 0
    assert stats["max_gray"] == 255
    assert stats["overexposed_pixels"] == 2
    assert stats["overexposed_ratio"] == 33.33


if __name__ == "__main__":
    test_calculate_image_stats_counts_saturated_pixels()
    print("test passed")
