
import cv2
from pathlib import Path
import random
import re

def scale_image(image):
  img = cv2.imread(str(image))

  # 如果路径错误或图片损坏，cv2.imread 会返回 None
  if img is None:
    return None

  scale = 0.2
  height,width = img.shape[:2]
  small = cv2.resize(img,(int(width*scale),int(height*scale)))
  # gray 暂时没有使用到，后面做阈值分割时会用到灰度图
  # gray = cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)

  return small

def is_valid_roi(x1,y1,x2,y2,width,height):
  """检查 ROI 坐标是否合法。

  x1,y1 是左上角；x2,y2 是右下角。
  必须保证左上角在右下角之前，并且不能超出图片范围。
  """
  return 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height

def roi_input():
  while True:
    roi_input = input("请输入ROI区域，格式 x1:y1,x2:y2，例如 100:80,300:220：")
    pattern = r"^\d+:\d+,\d+:\d+$"
    # 判断输入的格式是否正确
    if re.match (pattern,roi_input):
      first,second = roi_input.split(",")
      x1,y1 = map(int,first.split(":"))
      x2,y2 = map(int,second.split(":"))
      return x1,y1,x2,y2
    else:
      print("格式输入错误，请重新输入！")
  


BASE_DIR = Path(__file__).resolve().parent
images = BASE_DIR/"images"

# 找到文件夹下所有png图片
image_files = [
  img for img in images.iterdir()
  if img.is_file() and img.suffix.lower() in {".png", ".jpg", ".jpeg"}
]

if not image_files:
  raise FileNotFoundError("images 文件夹下没有找到 png/jpg/jpeg 图片")

roi_dir = BASE_DIR/"outputs"/"roi"
roi_dir.mkdir(parents=True, exist_ok=True)

# 随机抽选一张图片
random_image = random.choice(image_files)
# 按比例缩小
small = scale_image(random_image)

if small is None:
  raise RuntimeError(f"图片读取失败：{random_image}")

# 显示图片
cv2.imshow("image",small)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 定义裁剪的区域坐标
x1,y1,x2,y2 = 0,0,0,0
while True:
  # 调用函数 获取x1 y1 x2 y2
  x1,y1,x2,y2 = roi_input()
  height,width = small.shape[:2]

  if not is_valid_roi(x1,y1,x2,y2,width,height):
    print("ROI 坐标超出图片范围，或左上角/右下角顺序不正确，请重新输入。")
    continue

  # OpenCV/Numpy 裁剪顺序是 [y1:y2, x1:x2]
  roi_img = small[y1:y2,x1:x2]
  cv2.imshow("image",roi_img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  
  text = input("裁剪效果是否满意：(y/n)")
  if text == "y":
    break


for image in image_files:
  # 读取图片
  small = scale_image(image)
  if small is None:
    print("读取失败，跳过：", image)
    continue

  # 截取ROI区域
  roi = small[y1:y2,x1:x2]
  save_path = roi_dir/image.name
  cv2.imwrite(str(save_path),roi)


    
