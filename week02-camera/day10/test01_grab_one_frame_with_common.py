# -- coding: utf-8 --
"""
Day10 第 2 节：使用 camera_common 抓取一帧。
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
WEEK02_DIR = BASE_DIR.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "common_grab_one_frame"
OUTPUT_IMAGE_PATH = OUTPUT_DIR / "day10_common_grab_one_frame.png"

if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from camera_common.hik_mvs import grab_one_frame
from camera_common.image_stats import calculate_gray_stats


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image = grab_one_frame(device_index=0, exposure_time_us=1000.0)
    stats = calculate_gray_stats(image)

    saved = cv2.imwrite(str(OUTPUT_IMAGE_PATH), image)
    if not saved:
        raise RuntimeError(f"保存图片失败：{OUTPUT_IMAGE_PATH}")

    print("=== Day10 公共模块抓图验证 ===")
    print(f"图像 shape：{image.shape}")
    print(
        f"宽={stats['width']} 高={stats['height']} "
        f"mean={stats['mean_gray']:.2f} "
        f"min={stats['min_gray']} max={stats['max_gray']} "
        f"overexposed={stats['overexposed_ratio']:.2f}%"
    )
    print(f"保存路径：{OUTPUT_IMAGE_PATH}")


if __name__ == "__main__":
    main()
