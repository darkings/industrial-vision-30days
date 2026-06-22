"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-22 17:08:24
LastEditTime: 2026-06-22 17:09:04
"""

from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "contour_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "bounding_rect"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_name = IMAGE_FILE_PATH.stem
bounding_rect_path = OUTPUTS_PATH / f"{image_name}_bounding_rect.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片加载失败！")
# 灰度化
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# OTSU正二值化
usedthreshold, binary_image = cv2.threshold(
    gray_image,  # 输入灰色通道图
    0,  # OTSU自动阈值设置为0
    255,  # 最大值
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,  # OTSU 二值图
)
print(f"OTSU自动阈值为：{usedthreshold}")
# 找到全部轮廓
contours, hierarchy = cv2.findContours(
    binary_image,  # 输入OTSU二值图
    cv2.RETR_EXTERNAL,  # 只关注最外层轮廓
    cv2.CHAIN_APPROX_SIMPLE,  # 忽略冗余坐标
)

# 使用面积阈值1000来过滤噪点
min_area = 1000
valid_contours = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area >= min_area:
        valid_contours.append(contour)

# 为候选轮廓计算水平外接矩形
marked_image = image.copy()
for index, contour in enumerate(valid_contours):
    area = cv2.contourArea(contour)
    # 获取外接矩形
    x, y, width, height = cv2.boundingRect(contour)
    # 在marked_image 绘制矩形
    cv2.rectangle(
        marked_image,  # 在哪个图片上绘制
        (x, y),  # 左上角坐标
        (x + width, y + height),  # 右下角坐标
        (0, 255, 0),  # 绿色矩形
        1,
        cv2.LINE_AA,
    )
    # 标注编号 宽高和长宽比
    if height > 0:
        aspect_ratio = width / height
    else:
        aspect_ratio = 0
    marked_label = f"{index + 1} {width}x{height} {aspect_ratio:.2f}"

    cv2.putText(
        marked_image,
        marked_label,
        (x, max(y - 10, 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
        cv2.LINE_AA,
    )
    print(
        f"编号：{index + 1} 长：{width} 高：{height} 长宽比：{aspect_ratio:.2f} 面积：{area:.2f} 左上角坐标：{x},{y}"
    )
print(f"最终候选目标数量：{len(valid_contours)}")
# 保存
saved_marked = cv2.imwrite(str(bounding_rect_path), marked_image)

if saved_marked:
    print(f"{bounding_rect_path.name} 保存成功！")
else:
    print(f"{bounding_rect_path.name} 保存失败！")
