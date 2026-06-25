"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-24 16:13:12
LastEditTime: 2026-06-24 16:14:25
"""

from pathlib import Path

import cv2

# 路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "measurement_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "pixel_measurement"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
result_path = OUTPUTS_PATH / f"{image_name}_result.png"

# 读取图片并复制
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("文件读取失败")
marked_image = image.copy()
# 读取灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 二值化
_, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)
# 查找外部轮廓
contours, _ = cv2.findContours(
    binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)
# 过滤有效轮廓
min_area = 1000
valid_contours = []
for contour in contours:
    area = cv2.contourArea(contour)
    x, y, width, height = cv2.boundingRect(contour)
    if area >= min_area:
        valid_contours.append((contour, x, y, width, height))

# 根据x坐标排序，x坐标最小的最靠前
valid_contours.sort(key=lambda item: item[1])

# 排序第一个为标准件 第二个为带测量件
standard_part = valid_contours[0]
target_part = valid_contours[1]

standard_part_width_mm = 50


mm_per_pixel = standard_part_width_mm / standard_part[3]

standard_part_height_mm = standard_part[4] * mm_per_pixel

target_part_width_mm = target_part[3] * mm_per_pixel
target_part_height_mm = target_part[4] * mm_per_pixel

# 标准件画框和标注文字
cv2.rectangle(
    marked_image,
    (standard_part[1], standard_part[2]),
    (standard_part[1] + standard_part[3], standard_part[2] + standard_part[4]),
    (0, 255, 0),
    2,
    cv2.LINE_AA,
)
# 绘制文字
standard_texts = [
    "Standard",
    f"W:{standard_part_width_mm:.1f}mm",
    f"H:{standard_part_height_mm:.1f}mm",
    f"Scale:{mm_per_pixel:.4f}mm/px",
]
standard_text_x = standard_part[1]
standard_text_y = max(standard_part[2] - 75, 30)
# 循环标注文字
for index, text in enumerate(standard_texts):
    cv2.putText(
        marked_image,
        text,
        (standard_text_x, standard_text_y + index * 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
    )

# 待测量件画框和标注文字
cv2.rectangle(
    marked_image,
    (target_part[1], target_part[2]),
    (target_part[1] + target_part[3], target_part[2] + target_part[4]),
    (0, 255, 255),
    2,
    cv2.LINE_AA,
)

target_texts = [
    "Target",
    f"W:{target_part_width_mm:.1f}mm",
    f"H:{target_part_height_mm:.1f}mm",
    f"Scale:{mm_per_pixel:.4f}mm/px",
]
target_text_x = target_part[1]
target_text_y = max(target_part[2] - 75, 30)
for index, text in enumerate(target_texts):
    cv2.putText(
        marked_image,
        text,
        (target_text_x, target_text_y + index * 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 255),
        1,
    )

# 保存
saved = cv2.imwrite(str(result_path), marked_image)
if saved:
    print(f"{result_path.name} 保存成功")
else:
    print(f"{result_path.name} 保存失败")
