'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-18 15:32:56
LastEditTime: 2026-06-18 16:03:30
'''
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9852.png"

OUTPUTS_FILE_PATH = BASE_DIR/"outputs"/"brightness"
OUTPUTS_FILE_PATH.mkdir(parents=True,exist_ok=True)
brighter_image_path = OUTPUTS_FILE_PATH/"IMG_9852_brighter.png"
adjusted_image_path = OUTPUTS_FILE_PATH/"IMG_9852_adjusted.png"
high_contrast_image_path = OUTPUTS_FILE_PATH/"IMG_9852_high_contrast.png"

image = cv2.imread(str(IMAGE_FILE_PATH))

if image is None:
  raise FileNotFoundError("文件读取失败")


# 只提高亮度
brighter_image =  cv2.convertScaleAbs(
  image,
  alpha=1,
  beta=20
)

# 只增强对比度
high_contrast_image = cv2.convertScaleAbs(
  image,
  alpha=1.8,
  beta =0
)

# 同时增强
adjusted_image = cv2.convertScaleAbs(
  image,
  alpha=1.8,
  beta=20
)

brighter_image_save = cv2.imwrite(str(brighter_image_path),brighter_image)
high_contrast_save = cv2.imwrite(str(high_contrast_image_path),high_contrast_image)
adjusted_save = cv2.imwrite(str(adjusted_image_path),adjusted_image)

if all((brighter_image_save,high_contrast_save,adjusted_save)):
  print("保存成功，路径为：",brighter_image_path)
  print("保存成功，路径为：",high_contrast_image_path)
  print("保存成功，路径为：",adjusted_image_path)
else:
  print("保存失败")