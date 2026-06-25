from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

output_path = IMAGE_DIR / "rotated_rect_test.png"

image = np.zeros((520, 760, 3), dtype=np.uint8)


def draw_rotated_rect(center, size, angle, color=(255, 255, 255)):
    rect = (center, size, angle)
    box = cv2.boxPoints(rect)
    box = box.astype(int)
    cv2.drawContours(image, [box], 0, color, -1)


# 水平长条：boundingRect 与 minAreaRect 的尺寸接近
draw_rotated_rect((180, 130), (180, 60), 0)

# 倾斜长条：用于观察水平框会包含大量空白区域
draw_rotated_rect((500, 140), (220, 55), 28)

# 竖向倾斜零件：用于观察 width/height 和 angle 的变化
draw_rotated_rect((210, 380), (70, 210), -35)

# 接近正方形的旋转目标：用于观察角度和宽高解释并不总是直观
draw_rotated_rect((520, 370), (130, 120), 42)

# 小噪点：用于面积过滤
cv2.circle(image, (690, 70), 7, (255, 255, 255), -1)
cv2.rectangle(image, (660, 250), (680, 265), (255, 255, 255), -1)
cv2.circle(image, (350, 450), 5, (255, 255, 255), -1)

saved = cv2.imwrite(str(output_path), image)

if saved:
    print(f"{output_path.name} 保存成功！")
else:
    print(f"{output_path.name} 保存失败")
