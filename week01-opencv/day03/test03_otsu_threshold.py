'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-21 09:58:34
LastEditTime: 2026-06-21 10:21:52
'''
import cv2
from pathlib import Path

# 文件夹路径
BASE_DIR=Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"
OTSU_FILE_PATH = BASE_DIR/"outputs"/"otsu_threshold"
OTSU_FILE_PATH.mkdir(parents=True,exist_ok=True)

gray_path = OTSU_FILE_PATH/"IMG_9859_gray.png"
otsu_path = OTSU_FILE_PATH/"IMG_9859_otsu.png"
otsu_inv_path = OTSU_FILE_PATH/"IMG_9859_otsu_inv.png"
# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("图片加载失败")
# 转为灰度图
gray_image = cv2.cvtColor(
  image,
  cv2.COLOR_BGR2GRAY
)
# 生成OTSU正二值图
# otsu_threshold 自动计算的阈值
# binary_image 二值化图片
otsu_threshold,binary_image = cv2.threshold(
  gray_image, # 单通道灰度图
  0, # OTSU自动计算
  255, # 最大值
  cv2.THRESH_BINARY | cv2.THRESH_OTSU # OTSU 二值图
)

# 生成OTSU反二值图
# otsu_inv_threshold 自动计算的阈值
# binary_inv_image 二值图
otsu_inv_threshold,binary_inv_image = cv2.threshold(
  gray_image, # 单通道灰度图
  0,  # OTSU自动计算
  255, # 最大值
  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU # OTSU 反二值图
)

# 保存图片
gray_save = cv2.imwrite(str(gray_path),gray_image)
otsu_save = cv2.imwrite(str(otsu_path),binary_image)
otsu_inv_save = cv2.imwrite(str(otsu_inv_path),binary_inv_image)

saved_results = [
  (gray_save,gray_path),
  (otsu_save,otsu_path),
  (otsu_inv_save,otsu_inv_path),
]

for saved, file_path in saved_results:
  if saved :
    print(f"{file_path.name}保存成功")
  else:
    print(f"{file_path.name}保存失败")

# 输出两次自动阈值
print("OTSU正二值图阈值：",otsu_threshold," OTSU反二值图阈值：",otsu_inv_threshold)