'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-18 16:25:59
LastEditTime: 2026-06-18 17:07:25
'''
import cv2
from pathlib import Path
import matplotlib.pyplot as plt

# 当前路径
BASE_DIR = Path(__file__).resolve().parent
# 输入文件路径
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"

image_name = IMAGE_FILE_PATH.stem
# 输出文件路径
OUTPUTS_FILE_PATH = BASE_DIR/"outputs"/"histogram"
OUTPUTS_FILE_PATH.mkdir(parents=True,exist_ok=True)
# 每种结果定义不同文件名
gray_path = OUTPUTS_FILE_PATH / f"{image_name}_gray.png"
equalized_path = OUTPUTS_FILE_PATH / f"{image_name}_equalized.png"
clahe_path = OUTPUTS_FILE_PATH / f"{image_name}_clahe.png"
histogram_path = OUTPUTS_FILE_PATH / f"{image_name}_histograms.png"
# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("图片读取失败")
# 转灰度图
gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

# 进行全局直方图均衡化
equalized_image = cv2.equalizeHist(gray_image)

# 创建CLAHE对象
# cliplimit 限制局部对比度的增强幅度。数值越大越明显，越容易放大噪声
# tileGridSize 将图片划分为 几乘几的区域进行处理
clahe = cv2.createCLAHE(
  clipLimit=2.0,
  tileGridSize=(12,12)
)

# 对灰度图进行CLAHE局部均衡化
clahe_image = clahe.apply(gray_image)

# 计算原始灰度图的直方图
histogram_gray = cv2.calcHist(
  [gray_image],
  [0],
  None,
  [256],
  [0,256]
)

# 计算全局均衡化后的直方图
histogram_equalized = cv2.calcHist(
  [equalized_image],
  [0],
  None,
  [256],
  [0,256]
)

# 计算CLAHE处理后的直方图
histogram_clahe = cv2.calcHist(
  [clahe_image],
  [0],
  None,
  [256],
  [0,256]
)

# 创建画布
plt.figure(figsize=(12,6))

# 绘制原始灰度图直方图
plt.plot(
  histogram_gray,
  color="black",
  label="histogram gray"
)

# 绘制全局均衡化直方图
plt.plot(
  histogram_equalized,
  color="blue",
  label="histogram equalized"
)

# 绘制clahe处理过的直方图
plt.plot(
  histogram_clahe,
  color="green",
  label="histogram clahe"
)

# 设置画布标题
plt.title("gray histogram comparison")
# 设置横轴名称
plt.xlabel("gray value")
# 设置纵轴名称
plt.ylabel("pixel count")
# 限制横轴显示范围 0~255
plt.xlim([0,255])
# 显示图例
plt.legend()
# 显示网络
plt.grid(True)
# 自动调整图标边距
plt.tight_layout()

# 将直方图保存为图片
plt.savefig(str(histogram_path))
# 关闭画布
plt.close()

# 保存3张灰度图处理结果
gray_saved = cv2.imwrite(str(gray_path),gray_image)
equalized_saved = cv2.imwrite(str(equalized_path),equalized_image)
clahe_Saved = cv2.imwrite(str(clahe_path),clahe_image)

if all((gray_saved,equalized_saved,clahe_Saved)):
  print("保存成功！")
else:
  print("保存失败")

print("彩色图shape：", image.shape)
print("灰度图shape：", gray_image.shape)

print("原图直方图shape：", histogram_gray.shape)
print("全局均衡直方图shape：", histogram_equalized.shape)
print("CLAHE直方图shape：", histogram_clahe.shape)