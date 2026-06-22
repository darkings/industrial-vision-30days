"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-22 10:40:54
LastEditTime: 2026-06-22 10:41:19
"""

from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "canny_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "canny_basics"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
gray_path = OUTPUTS_PATH / f"{image_name}_gray.png"
gaussian_path = OUTPUTS_PATH / f"{image_name}_gaussian.png"
edge_raw_path = OUTPUTS_PATH / f"{image_name}_edge_raw.png"
edge_gaussian_path = OUTPUTS_PATH / f"{image_name}_edge_gaussian.png"

# 统一Canny参数
threshold1 = 50
threshold2 = 150

# 读取灰度图
gray_image = cv2.imread(str(IMAGE_FILE_PATH), cv2.IMREAD_GRAYSCALE)

if gray_image is None:
    raise FileNotFoundError("灰度图读取失败")

# 执行Canny
edge_raw_image = cv2.Canny(
    gray_image,  # 输入单通道灰度图
    threshold1,  # 低阈值
    threshold2,  # 高阈值
)
# 计算执行Canny后的边缘像素
edge_raw_pixels = cv2.countNonZero(edge_raw_image)
# 打印
print(f"执行Canny后的边缘像素数量：{edge_raw_pixels}")
# 使用5x5 高斯滤波
blurred_image = cv2.GaussianBlur(
    gray_image,  # 输入单通道灰度图
    (5, 5),  # 5x5的卷积核
    0,  # OpenCV根据核尺寸自动计算sigmaX
)

# 对滤波图执行相同参数的Canny
edge_gaussian_image = cv2.Canny(
    blurred_image,  # 输入高斯滤波后的灰度图
    threshold1,  # 低阈值
    threshold2,  # 高阈值
)
# 计算高斯滤波后执行Canny的边缘像素
edge_gaussian_pixels = cv2.countNonZero(edge_gaussian_image)
# 打印
print(f"执行高斯滤波后再执行Canny后的边缘像素数量：{edge_gaussian_pixels}")
# 保存
saved_gray = cv2.imwrite(str(gray_path), gray_image)
saved_gaussian = cv2.imwrite(str(gaussian_path), blurred_image)
saved_edge_raw = cv2.imwrite(str(edge_raw_path), edge_raw_image)
saved_edge_gaussian = cv2.imwrite(str(edge_gaussian_path), edge_gaussian_image)
# 打印
saved_results = [
    [saved_gray, gray_path],
    [saved_gaussian, gaussian_path],
    [saved_edge_raw, edge_raw_path],
    [saved_edge_gaussian, edge_gaussian_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功")
    else:
        print(f"{path.name} 保存失败")
