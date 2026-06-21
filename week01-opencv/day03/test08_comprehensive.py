"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-21 23:21:10
LastEditTime: 2026-06-21 23:21:16
"""

from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "day03_comprehensive_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "comprehensive"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_name = IMAGE_FILE_PATH.stem
gray_path = OUTPUTS_PATH / f"{image_name}_gray.png"
binary_path = OUTPUTS_PATH / f"{image_name}_binary.png"
opened_path = OUTPUTS_PATH / f"{image_name}_opened.png"
final_path = OUTPUTS_PATH / f"{image_name}_final.png"

# 读取灰度图
gray_image = cv2.imread(str(IMAGE_FILE_PATH), cv2.IMREAD_GRAYSCALE)
if gray_image is None:
    raise FileNotFoundError("图片读取失败")

saved_gray = cv2.imwrite(str(gray_path), gray_image)

# 二值化 区分背景和前景
used_threshold, binary_image = cv2.threshold(
    gray_image,  # 单通道灰度图
    0,  # 自动计算阈值，人工设置为0
    255,  # 最大值
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,  # OTSU 正二值图
)

print(f"OTSU 自动计算阈值：{used_threshold}")
binary_white_pixels = cv2.countNonZero(binary_image)
print(f"{binary_path.name} 白色像素数量为：{binary_white_pixels}")
saved_binary = cv2.imwrite(str(binary_path), binary_image)

# 创建结构元素
kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,  # 矩形结构核
    (3, 3),  # 3x3 核大小
)

# 开运算 先腐蚀后膨胀
# 先腐蚀掉白色噪点和白色毛刺
# 再膨胀区域到原大小
# 开运算可能删除真实的白色小缺陷。
opened_image = cv2.morphologyEx(
    binary_image,  # 正二值图
    cv2.MORPH_OPEN,  # 开运算
    kernel,  # 结构元素
    iterations=1,  # 开运算1次
)
opened_white_pixels = cv2.countNonZero(opened_image)
print(f"{opened_path.name} 白色像素数量为：{opened_white_pixels}")
saved_opened = cv2.imwrite(str(opened_path), opened_image)

# 当前背景的白色噪点和毛刺消失
# 下一步去除前景里的黑色裂缝和黑色小孔
# 去除黑色裂缝和小孔，需要将白色前景膨胀掩盖住黑色裂缝和黑色小孔
# 再进行腐蚀，将前景恢复到原来大小
# 膨胀 -> 腐蚀 所以需要在已经开运算的图片上再次进行闭运算
# 闭运算可能填掉需要检测的黑色小缺陷。
closed_image = cv2.morphologyEx(
    opened_image,  # 已经开运算的图片
    cv2.MORPH_CLOSE,  # 进行闭运算
    kernel,  # 结构元素
    iterations=1,  # 闭运算1次
)

closed_white_pixels = cv2.countNonZero(closed_image)
print(f"{final_path.name} 白色像素数量为：{closed_white_pixels}")
saved_closed = cv2.imwrite(str(final_path), closed_image)

# 通过图片查看到图片已经去除背景的噪点和毛刺。前景的小孔和裂缝
# 打印
saved_results = [
    [saved_gray, gray_path],
    [saved_binary, binary_path],
    [saved_opened, opened_path],
    [saved_closed, final_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败")
