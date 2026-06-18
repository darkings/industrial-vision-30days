'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-18 14:21:52
LastEditTime: 2026-06-18 15:20:51
'''
from pathlib import Path
import cv2

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9851.png"

OUTPUTS_FILE_PATH = BASE_DIR/"outputs"/"filters"
OUTPUTS_FILE_PATH.mkdir(parents=True,exist_ok=True)
mean_output_path = OUTPUTS_FILE_PATH / "IMG_9851_mean.png"
gaussian_output_path = OUTPUTS_FILE_PATH / "IMG_9851_gaussian.png"
median_output_path = OUTPUTS_FILE_PATH / "IMG_9851_median.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))

if image is None:
  raise FileNotFoundError("文件读取失败")

# 复制图片
filters_image = image.copy()
# 滤波核
kernel=(5,5)
# 中值滤波
median_kernel = 5

# 均值滤波图片
mean_image = cv2.blur(filters_image,kernel)
cv2.imshow("image",mean_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
mean_save = cv2.imwrite(str(mean_output_path),mean_image)
if mean_save :
  print("图片保存成功，保存路径：",mean_output_path)
else:
  print("保存失败！")

# 高斯滤波图片
gaussian_image = cv2.GaussianBlur(filters_image,kernel,0)
cv2.imshow("image",gaussian_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
gaussian_save = cv2.imwrite(str(gaussian_output_path),gaussian_image)
if gaussian_save :
  print("图片保存成功，保存路径：",gaussian_output_path)
else:
  print("保存失败！")
  
# 中值滤波图片
median_image = cv2.medianBlur(filters_image,median_kernel)
cv2.imshow("image",median_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
median_save = cv2.imwrite(str(median_output_path),median_image)
if median_save :
  print("图片保存成功，保存路径：",median_output_path)
else:
  print("保存失败！")
  