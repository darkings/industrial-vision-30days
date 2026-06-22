"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-22 15:13:56
LastEditTime: 2026-06-22 15:14:14
"""

from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "contour_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "find_draw_contours"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_name = IMAGE_FILE_PATH.stem
binary_path = OUTPUTS_PATH / f"{image_name}_binary.png"
contours_path = OUTPUTS_PATH / f"{image_name}_contours.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片读取失败")

# 转灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# OTSU 正二值化
used_threshold, binary_image = cv2.threshold(
    gray_image,  # 输入的单通道灰度图
    0,  # OTSU自动阈值
    255,  # 最大值
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,  # OTSU 正二值化
)
print(f"{binary_path.name} 的OTSU自动阈值为：{used_threshold}")
# 查找全部外轮廓
contours, hierarchy = cv2.findContours(
    binary_image,  # 输入的单通道图片 当前为OTSU正二值图
    cv2.RETR_EXTERNAL,  # 表示只查找外层轮廓
    cv2.CHAIN_APPROX_SIMPLE,  # 表示压缩轮廓中的冗余坐标
)
if hierarchy is not None:
    print(f"hierarchy shape：{hierarchy.shape}")

# 绿色在复制图上绘制全部轮廓
marked_image = image.copy()


cv2.drawContours(
    marked_image,  # 输入的原图复制图。用于在输入图中绘制轮廓
    contours,  # 查找到的所有轮廓
    -1,  # 表示绘制全部轮廓
    (0, 255, 0),  # 绘制的轮廓颜色 当前为绿色
    2,  # 线条粗细
)
# 保存二值图和标注图
saved_binary = cv2.imwrite(str(binary_path), binary_image)
saved_marked = cv2.imwrite(str(contours_path), marked_image)

saved_results = [[saved_binary, binary_path], [saved_marked, contours_path]]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败！")
# 输出轮廓数量和每条轮廓的shape
if not contours:
    print("没有找到轮廓")

print(f"查找到的轮廓数量为：{len(contours)}")
for index, contour in enumerate(contours):
    print(f"第{index + 1}条的shape为：{contour.shape}")
