"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-22 16:10:03
LastEditTime: 2026-06-22 16:10:54
"""

from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "contour_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "contour_area_perimeter"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_name = IMAGE_FILE_PATH.stem
all_contours_path = OUTPUTS_PATH / f"{image_name}_all_contours.png"
filtered_contours_path = OUTPUTS_PATH / f"{image_name}_filtered_contours.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片加载失败！")
# 转灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# OTSU 正二值化
used_threshold, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)

# 查找全部轮廓
contours, hierarchy = cv2.findContours(
    binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

# 计算每条轮廓闭合周长和面积
min_area = 1000
valid_contours = []
# 循环
for index, contour in enumerate(contours):
    # 获取周长和面积
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    print(f"第{index + 1}条轮廓的周长为{perimeter:.2f},面积为{area:.2f}")
    # 如果当前轮廓面积大于最小面积，将当前轮廓添加到候选轮廓序列中
    if area >= min_area:
        valid_contours.append(contour)
# 打印原始轮廓数量和过滤后的候选轮廓数量
print(f"原始轮廓数量：{len(contours)}")
print(f"过滤后的候选轮廓数量：{len(valid_contours)}")

# 复制原图
all_contours_image = image.copy()
filtered_contours_image = image.copy()
# 绘制标注全部轮廓图和标注过滤后的候选轮廓图
cv2.drawContours(
    all_contours_image,  # 传入全部轮廓图
    contours,  # 传入全部轮廓
    -1,  # 所有轮廓
    (0, 0, 255),  # 红色标注
    2,  # 标注线条粗细为2
)

cv2.drawContours(
    filtered_contours_image,  # 传入候选轮廓图
    valid_contours,  # 传入候选轮廓
    -1,  # 标注全部轮廓
    (0, 255, 0),  # 绿色标注
    2,  # 标注线条粗细为2
)

# 保存
saved_all_contours = cv2.imwrite(str(all_contours_path), all_contours_image)
saved_filtered_contours = cv2.imwrite(
    str(filtered_contours_path), filtered_contours_image
)

saved_results = [
    [saved_all_contours, all_contours_path],
    [saved_filtered_contours, filtered_contours_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败！")
