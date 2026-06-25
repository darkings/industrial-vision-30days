from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

output_path = IMAGE_DIR / "pipeline_test.png"

# Day06 第一节：综合流程预览图
# 目标：让 OTSU、形态学、轮廓查找、面积过滤都能看到效果。
image = np.zeros((520, 760, 3), dtype=np.uint8)

# 轻微不均匀背景，模拟现场背景不可能绝对纯黑
for y in range(image.shape[0]):
    value = 18 + int(y / image.shape[0] * 18)
    image[y, :, :] = (value, value, value)

# 三个主要白色工件
cv2.rectangle(image, (80, 90), (250, 220), (235, 235, 235), -1)
cv2.rectangle(image, (430, 85), (630, 215), (235, 235, 235), -1)

# 一个倾斜工件
rect = ((230, 390), (210, 75), -25)
box = cv2.boxPoints(rect).astype(int)
cv2.drawContours(image, [box], 0, (235, 235, 235), -1)

# 小白噪点：应被面积过滤或开运算削弱
cv2.circle(image, (690, 75), 7, (255, 255, 255), -1)
cv2.circle(image, (365, 260), 5, (255, 255, 255), -1)
cv2.rectangle(image, (650, 365), (670, 380), (255, 255, 255), -1)

# 工件上的小孔/黑点：用于提醒形态学会影响细节
cv2.circle(image, (165, 155), 10, (25, 25, 25), -1)
cv2.rectangle(image, (520, 140), (545, 165), (25, 25, 25), -1)

saved = cv2.imwrite(str(output_path), image)

if saved:
    print(f"{output_path.name} 保存成功！")
else:
    print(f"{output_path.name} 保存失败")
