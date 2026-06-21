import cv2
from pathlib import Path


# 文件夹路径
BASE_DIR=Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9859.png"
THRESHOLD_FILE_PATH = BASE_DIR/"outputs"/"fixed_threshold"
THRESHOLD_FILE_PATH.mkdir(parents=True,exist_ok=True)
# 文件路径
gray_path = THRESHOLD_FILE_PATH/"IMG_9859_gray.png"
binary_path = THRESHOLD_FILE_PATH/"IMG_9859_binary.png"
binary_inv_path = THRESHOLD_FILE_PATH/"IMG_9859_binary_inv.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("文件读取失败")
# 转为灰度图
gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
# 阈值
thresh =127
# 使用固定阈值生成正二值图
# binary_threshold 实际使用阈值
# binary_image 二值化图片
binary_threshold,binary_image = cv2.threshold(
  gray_image, # 灰度图
  thresh, # 固定阈值
  255, # 最大值
  cv2.THRESH_BINARY # 转化方式 当前为正二值化
)
# 使用相同阈值生成反二值图
# binary_inv_threshold 实际使用的阈值
# binary_inv_image 生成的二值化图片
binary_inv_threshold,binary_inv_image = cv2.threshold(
  gray_image, # 灰度图
  thresh, # 固定阈值
  255, # 最大值
  cv2.THRESH_BINARY_INV # 转化方式 当前为反二值化
)
# 保存三张结果图
gray_save = cv2.imwrite(str(gray_path),gray_image)
binary_save = cv2.imwrite(str(binary_path),binary_image)
binary_inv_save = cv2.imwrite(str(binary_inv_path),binary_inv_image)
if all((gray_save,binary_save,binary_inv_save)):
  print("保存成功")
else:
  print("保存失败")
# 输出的实际阈值
print("实际阈值分别为：",binary_threshold,"、",binary_inv_threshold)