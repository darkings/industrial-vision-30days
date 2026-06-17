'''
Descripttion: 练习1：图片读取
Author: Jie.Zh
Date: 2026-06-17 09:34:15
LastEditTime: 2026-06-17 14:22:50
'''

from pathlib import Path
import cv2

# __file__ 表示当前这个文件夹本身
# resolve() 会把路径转化为绝对路径
# parent 表示当前Python文件所在的文件夹
BASE_DIR = Path(__file__).resolve().parent
images = BASE_DIR/"images"

# 只处理这些图片后缀，避免把文件夹或其他文件交给 cv2.imread
image_suffixes = {".png", ".jpg", ".jpeg"}

for img_path in images.iterdir():
    # is_file 是函数，需要加括号调用；suffix 是文件后缀，例如 ".png"
    if not img_path.is_file() or img_path.suffix.lower() not in image_suffixes:
        continue

    image = cv2.imread(str(img_path))

    # 图片读取失败时，cv2.imread 会返回 None
    if image is None:
        print("读取失败：", img_path)
        continue

    # 文件名
    print("文件名：", img_path.name)

    # shape 返回顺序是：高度、宽度、通道数
    image_shape = image.shape
    print("shape：", image_shape)

    height, width, channel = image_shape[:3]

    # 宽度
    print("宽度：", width)
    # 高度
    print("高度：", height)
    # 通道数
    print("通道数：", channel)
    # 图片的分辨率
    print("分辨率：", width, "x", height)
    # 中心的像素值，注意访问像素时是 image[y, x]
    print("中心点像素值：", image[height // 2, width // 2])
    print("-" * 30)

