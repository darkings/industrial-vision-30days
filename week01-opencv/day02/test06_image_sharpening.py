import cv2
from pathlib import Path

# 当前路径
BASE_DIR = Path(__file__).resolve().parent
# 输入图片
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9855.png"
image_name = IMAGE_FILE_PATH.stem
# 输出文件夹
OUTPUT_FILE_PATH = BASE_DIR/"outputs"/"sharpened"
OUTPUT_FILE_PATH.mkdir(parents=True,exist_ok=True)
# 不同结果创建不同路径
blurred_path = OUTPUT_FILE_PATH/f"{image_name}_blurred.png"
sharpened_path = OUTPUT_FILE_PATH/f"{image_name}_sharpened.png"
strong_sharpened_path = OUTPUT_FILE_PATH/f"{image_name}_strong_sharpened.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
  raise FileNotFoundError("图片加载失败")
# 高斯滤波生成模糊图
# 用于图片中的低频，平缓区域
blurred_image = cv2.GaussianBlur(
  image,
  (7,7),
  0
)
# 普通锐化
sharpened_image = cv2.addWeighted(
  image,
  1.5,
  blurred_image,
  -0.5,
  0
)
# 更强锐化
strong_sharpened_image = cv2.addWeighted(
  image,
  2.0,
  blurred_image,
  -1,
  0
)

# 保存模糊图
saved_blurred = cv2.imwrite(str(blurred_path),blurred_image)
# 保存普通锐化图
save_sharpened = cv2.imwrite(str(sharpened_path),sharpened_image)
# 保存更强锐化图
save_strong_sharpened = cv2.imwrite(str(strong_sharpened_path),strong_sharpened_image)

if all((save_sharpened,saved_blurred,save_strong_sharpened)):
  print("保存成功")
else:
  print("保存失败")