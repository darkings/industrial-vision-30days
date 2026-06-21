'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-20 22:45:03
LastEditTime: 2026-06-20 23:05:56
'''
import cv2
from pathlib import Path


# 文件夹路径
BASE_DIR=Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"
THRESHOLD_FILE_PATH = BASE_DIR/"outputs"/"threshold_comparison"
THRESHOLD_FILE_PATH.mkdir(parents=True,exist_ok=True)

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("文件读取失败")
# 转为灰度图
gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

threshold_values = [50,127,200]

# 循环
for threshold in threshold_values:
  used_threshold,binary_image = cv2.threshold(
    gray_image,
    threshold,
    255,
    cv2.THRESH_BINARY
  )

  # 保存文件
  binary_path = THRESHOLD_FILE_PATH/f"IMG_9859_binary_{threshold}.png"

  binary_save = cv2.imwrite(str(binary_path),binary_image)
  if binary_save :
    print("保存成功，路径为",str(binary_path))
  else:
    print(f"IMG_9859_binary_{threshold}.png 保存失败")
  print(f"IMG_9859_binary_{threshold}.png 的实际阈值为：",used_threshold)
  

  


