"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-21 22:52:36
LastEditTime: 2026-06-21 22:59:01
"""

from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "morphology_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "open_close"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_name = IMAGE_FILE_PATH.stem
original_path = OUTPUTS_PATH / f"{image_name}_original.png"
opened_path = OUTPUTS_PATH / f"{image_name}_opened.png"
closed_path = OUTPUTS_PATH / f"{image_name}_closed.png"

# 读取灰度图
gray_image = cv2.imread(str(IMAGE_FILE_PATH), cv2.IMREAD_GRAYSCALE)
if gray_image is None:
    raise FileNotFoundError("灰度图读取失败")
# 3x3 矩形结构元素
kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,  # 矩形结构元素
    (3, 3),  # 3x3 区域
)
# 开运算
opened_image = cv2.morphologyEx(
    gray_image,  # 单通道灰度图 白色区域为前景
    cv2.MORPH_OPEN,  # 形态学操作类型 当前为开运算
    kernel,  # 结构元素 3x3
    iterations=1,  # 开运算1次
)
# 闭运算
closed_image = cv2.morphologyEx(
    gray_image,  # 单通道灰度图。白色区域为前景
    cv2.MORPH_CLOSE,  # 形态学操作类型 当前为闭运算
    kernel,  # 结构元素 3x3
    iterations=1,  # 闭运算1次
)

# 保存3张图
saved_gray = cv2.imwrite(str(original_path), gray_image)
saved_opened = cv2.imwrite(str(opened_path), opened_image)
saved_closed = cv2.imwrite(str(closed_path), closed_image)

# 打印结果
saved_results = [
    [saved_gray, original_path],
    [saved_opened, opened_path],
    [saved_closed, closed_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功")
    else:
        print(f"{path.name} 保存失败")
