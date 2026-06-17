'''
Descripttion: 练习4：生成灰度图
Author: Jie.Zh
Date: 2026-06-17 14:23:33
LastEditTime: 2026-06-17 14:57:10
'''
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
images = BASE_DIR/"images"
gray_dir = BASE_DIR/"outputs"/"gray"
gray_dir.mkdir(parents=True, exist_ok=True)

image_suffixes = {".png", ".jpg", ".jpeg"}

for image_path in images.iterdir():
  # 只处理图片文件
  if not image_path.is_file() or image_path.suffix.lower() not in image_suffixes:
    continue

  # 读取图片
  img = cv2.imread(str(image_path))

  # 读取失败时直接跳过，避免后面 img.shape 报错
  if img is None:
    print("读取失败：", image_path)
    continue

  # 缩放图片
  scale = 0.2
  height,width = img.shape[:2]
  # resize 后面跟的是分辨率必须是整数
  small = cv2.resize(img,(int(width*scale),int(height*scale)))
  # 图片转灰度
  gray_img = cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
  # 观看图片
  # cv2.imshow("gray_img",gray_img)
  # cv2.waitKey(0)
  # 图片保存
  save_path = gray_dir/image_path.name
  cv2.imwrite(str(save_path),gray_img)

