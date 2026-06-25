"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-24 15:08:02
LastEditTime: 2026-06-24 15:08:20
"""

from pathlib import Path

import cv2

# 路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "rotated_rect_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "min_area_rect"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
original_path = OUTPUTS_PATH / f"{image_name}_original.png"
result_path = OUTPUTS_PATH / f"{image_name}_result.png"

# 读取图片并复制
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片读取失败")
marked_image = image.copy()
# 灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 二值化
used_threshold, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)
print(f"OTSU 阈值为：{used_threshold}")
# 查找外部轮廓
contours, hierarchy = cv2.findContours(
    binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)
# 过滤的最小区域
min_area = 1000
valid_index = 0

# 循环
for contour in contours:
    # 当前轮廓面积
    area = cv2.contourArea(contour)
    # 过滤有效轮廓
    if area >= min_area:
        valid_index += 1
        # 周长
        perimeter = cv2.arcLength(contour, True)
        # 水平外接矩形
        x, y, width, height = cv2.boundingRect(contour)
        # 旋转外接矩形
        rect = cv2.minAreaRect(contour)
        # 旋转矩形宽高、角度
        rotated_rect_width = rect[1][0]
        rotated_rect_height = rect[1][1]
        angle = rect[2]
        # 获取4个角点
        box = cv2.boxPoints(rect)
        # 将浮点类型转为int类型
        box = box.astype(int)
        # 画出水平外接矩形
        cv2.rectangle(
            marked_image,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            1,
        )
        # 画出旋转外接矩形
        cv2.drawContours(
            marked_image,
            [box],
            0,
            (0, 0, 255),
            1,
        )
        # 打印
        print(
            f"第{valid_index}个有效轮廓 周长为{perimeter}\n"
            f"水平矩形：尺寸 {width}x{height}\n"
            f"旋转矩形：尺寸 {rotated_rect_width:.2f}x{rotated_rect_width:.2f}  角度{angle}"
        )
# 保存
saved_original = cv2.imwrite(str(original_path), image)
saved_result = cv2.imwrite(str(result_path), marked_image)

saved_results = [
    [saved_original, original_path],
    [saved_result, result_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败")
