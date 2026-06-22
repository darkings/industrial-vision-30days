"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-22 11:09:17
LastEditTime: 2026-06-22 11:09:47
"""

from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "canny_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "canny_threshold_comparison"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
threshold_pairs = [(20, 60), (50, 150), (100, 200)]
# 读取灰度图
gray_image = cv2.imread(str(IMAGE_FILE_PATH), cv2.IMREAD_GRAYSCALE)
if gray_image is None:
    raise FileNotFoundError("灰度图读取失败")
# 循环threshold_pairs列表。每一轮分别取得低阈值low_threshold和高阈值high_threshold
for low_threshold, high_threshold in threshold_pairs:
    # 保存路径
    saved_path = (
        OUTPUTS_PATH / f"{image_name}_edges_{low_threshold}_{high_threshold}.png"
    )

    # Canny
    edge_image = cv2.Canny(
        gray_image,  # 输入单通道
        low_threshold,  # 低阈值
        high_threshold,  # 高阈值
    )
    # 边缘像素数量
    edge_pixels = cv2.countNonZero(edge_image)
    print(f"{saved_path.name} 边缘像素数量：{edge_pixels}")
    # 保存
    saved_edge = cv2.imwrite(str(saved_path), edge_image)
    if saved_edge:
        print(f"{saved_path.name} 保存成功")
    else:
        print(f"{saved_path.name} 保存失败")
