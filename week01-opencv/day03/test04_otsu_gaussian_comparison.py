'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-21 12:17:19
LastEditTime: 2026-06-21 13:08:26
'''
import cv2
from pathlib import Path

# 文件夹路径
BASE_DIR=Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"
OTSU_FILE_PATH = BASE_DIR/"outputs"/"otsu_gaussian_comparison"
OTSU_FILE_PATH.mkdir(parents=True,exist_ok=True)

# 文件路径
gray_path = OTSU_FILE_PATH/"IMG_9859_gray.png"
gaussian_path = OTSU_FILE_PATH/"IMG_9859_gaussian.png"
otsu_gaussian_path = OTSU_FILE_PATH/"IMG_9859_otsu_gaussian.png"
otsu_original_path = OTSU_FILE_PATH/"IMG_9859_otsu_original.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))

if image is None:
  raise FileNotFoundError("文件读取失败！")

# 转为灰度图
gray_image = cv2.cvtColor(
  image,
  cv2.COLOR_BGR2GRAY
)

# 灰度图执行otsu
otsu_gray_threshold,binary_image = cv2.threshold(
  gray_image,
  0,
  255,
  cv2.THRESH_BINARY | cv2.THRESH_OTSU
)

# 使用5x5卷积核高斯处理灰度图
gaussian_image = cv2.GaussianBlur(
  gray_image, # 单通道灰度图
  (5,5), # 卷积核 正奇数
  0 # 高斯分布在x方向的标准差 传入0 自动计算x的值
)

# 对高斯图执行OTSU
otsu_gaussian_threshold,binary_gaussian_image = cv2.threshold(
  gaussian_image,
  0,
  255,
  cv2.THRESH_BINARY|cv2.THRESH_OTSU
)

# 保存四张图片
gray_saved = cv2.imwrite(str(gray_path),gray_image)
otsu_gray_saved = cv2.imwrite(str(otsu_original_path),binary_image)
gaussian_saved = cv2.imwrite(str(gaussian_path),gaussian_image)
otsu_gaussian_saved = cv2.imwrite(str(otsu_gaussian_path),binary_gaussian_image)

results_saved = [
  [gray_saved,gray_path],
  [otsu_gaussian_saved,otsu_gaussian_path],
  [otsu_gray_saved,otsu_original_path],
  [gaussian_saved,gaussian_path]
]

for saved,path in results_saved:
  if saved:
    print(f"{path.name} 保存成功！")
  else:
    print(f"{path.name} 保存失败")
# 输出两个阈值
print(f"原始灰度图阈值：{otsu_gray_threshold}")
print(f"高斯滤波后阈值：{otsu_gaussian_threshold}")