'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-21 16:48:41
LastEditTime: 2026-06-21 17:21:41
'''
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"
OUTPUTS_FILE_PATH = BASE_DIR/"outputs"/"adaptive_threshold"
OUTPUTS_FILE_PATH.mkdir(parents=True,exist_ok=True)
image_name = IMAGE_FILE_PATH.stem
gray_path = OUTPUTS_FILE_PATH/f"{image_name}_gray.png"
adaptive_mean_path = OUTPUTS_FILE_PATH/f"{image_name}_adaptive_mean.png"
adaptive_gaussian_path = OUTPUTS_FILE_PATH/f"{image_name}_adaptive_gaussian.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("文件读取失败")
# 转为灰度图
gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

# 生成邻域均值自适应二值图
adaptive_mean_image = cv2.adaptiveThreshold(
  gray_image, # 单通道灰度图
  255, # 最大值
  cv2.ADAPTIVE_THRESH_MEAN_C, # 局部阈值的计算方法 当前为邻域均值
  cv2.THRESH_BINARY, # 正二值图
  11, # 局部区域大小 为大于1的奇数
  2 # 局部统计值中减去的常数C
)

# 生成高斯加权自适应二值图
adaptive_gaussian_image = cv2.adaptiveThreshold(
  gray_image, # 单通道灰度图
  255, # 最大值
  cv2.ADAPTIVE_THRESH_GAUSSIAN_C, # 局部阈值的计算方法 当前为高斯加权
  cv2.THRESH_BINARY, # 正二值图
  11, # 局部区域大小 为大于1的奇数
  2 # 局部统计值中减去的常数C
)

# 保存三张图片
saved_gray = cv2.imwrite(str(gray_path),gray_image)
saved_adaptive_mean = cv2.imwrite(str(adaptive_mean_path),adaptive_mean_image)
saved_adaptive_gaussian = cv2.imwrite(str(adaptive_gaussian_path),adaptive_gaussian_image)

saved_results = [
  [saved_gray,gray_path],
  [saved_adaptive_mean,adaptive_mean_path],
  [saved_adaptive_gaussian,adaptive_gaussian_path]
]

for saved,path in saved_results:
  if saved:
    print(f"{path.name} 保存成功！")
  else:
    print(f"{path.name} 保存失败！")