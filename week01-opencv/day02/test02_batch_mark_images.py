'''
Descripttion: 
Author: Jie.Zh
Date: 2026-06-18 10:48:49
LastEditTime: 2026-06-18 11:33:41
'''
import cv2
from pathlib import Path


# 所在目录路径
BASE_DIR = Path(__file__).resolve().parent
# 图片文件夹
IMAGES_FILE_PATH = BASE_DIR/"images"
# 输出文件夹
OUTPUTS_FILE_PATH = BASE_DIR/"outputs"/"marked"
OUTPUTS_FILE_PATH.mkdir(parents=True,exist_ok=True)
 # 允许的图片后缀
IMAGES_SUFFIX = {".png",".jpg",".jpeg"}

# 统计
success_count =0
error_count =0
skip_count=0

# 循环图片文件夹，获取所有图片
for image in IMAGES_FILE_PATH.iterdir():
  # 判断是否为文件并且扩展名是否为图片
  if image.is_file() and image.suffix.lower()  in IMAGES_SUFFIX:
    img = cv2.imread(str(image))
    if img is None:
      error_count+=1
      print(image.name,"读取失败！")
      continue
    # 开始对图片进行操作
    # 复制图片
    marked_img = img.copy()

    height,width = marked_img.shape[:2]
    # 画框
    half_box_size = 200
    x1 = max(width//2-half_box_size,0)
    y1 = max(height//2-half_box_size,0)
    x2 = min(width//2+half_box_size,width-1)
    y2 = min(height//2+half_box_size,height-1)

    cv2.rectangle(
      marked_img,
      (x1,y1),
      (x2,y2),
      (0,255,0),
      2
    )
    # 标注文字
    label_text="ROI"
    label_x = x1+5
    label_y = max(y1+30,200)

    cv2.putText(
      marked_img,
      label_text,
      (label_x,label_y),
      cv2.FONT_HERSHEY_SIMPLEX,
      1,
      (0,255,0),
      1,
      cv2.LINE_AA
    )

    # 保存文件 
    save_img = cv2.imwrite(str(OUTPUTS_FILE_PATH/image.name),marked_img)

    if save_img :
      print(image.name,"保存成功")
      success_count+=1
    else:
      print(image.name,"保存失败")
      error_count +=1
  else:
    skip_count+=1
    print(image.name,"不是一个图片，跳过")
    continue


print ("总数量：",str(skip_count+success_count+error_count))
print ("转化失败数量：",str(error_count))
print ("转化成功数量：",str(success_count))
print ("跳过数量：",str(skip_count))