import cv2
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent

# 图片路径
IMAGE_FILE_PATH = BASE_DIR/"images"/"IMG_9850.png"
# 输出基本路径
OUTPUTS_DIR = BASE_DIR/"outputs"/"marked"
OUTPUTS_DIR.mkdir(parents=True,exist_ok=True)
      
# 图片输出路径
OUTPUTS_IMAGE_PATH = OUTPUTS_DIR/"IMG_9850.png"

# 读取图片
image = cv2.imread(IMAGE_FILE_PATH)

if image is None:
  # 不能直接用print("图片读取失败")，因为会导致代码继续运行。图片读取不出来下面的copy也会报错
  # 用 直接抛出错误并终止程序
  raise FileNotFoundError("图片读取失败")


# 标记图片
marked_image = image.copy()
height,width = marked_image.shape[:2]

# 画框坐标
x1 = width//2 -200
x2 = width//2 +200
y1 = height//2 -200
y2 = height//2 +200

# 画框
cv2.rectangle(
  marked_image,
  (x1,y1),
  (x2,y2),
  (0,255,0),
  2
)

save_iamge = cv2.imwrite(
  str(OUTPUTS_IMAGE_PATH),
  marked_image
)

if save_iamge:
  print("保存成功，路径为：",OUTPUTS_IMAGE_PATH)
else:
  print("保存失败")