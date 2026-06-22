"""创建 Day 4 Canny 边缘检测练习图。"""

from pathlib import Path

import cv2
import numpy as np


DAY_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = DAY_DIR / "images" / "canny_test.png"

height = 480
width = 640
rng = np.random.default_rng(40)

# 创建带轻微横向亮度变化的暗灰背景。
background_line = np.linspace(35, 60, width, dtype=np.float32)
image = np.tile(background_line, (height, 1))

# 加入少量传感器噪声，用于观察高斯滤波对伪边缘的影响。
noise = rng.normal(0, 7, (height, width))
image = np.clip(image + noise, 0, 255).astype(np.uint8)

# 绘制一个亮色工业零件主体，外轮廓应形成强边缘。
cv2.rectangle(image, (150, 105), (490, 375), 190, -1)
cv2.rectangle(image, (255, 65), (385, 105), 190, -1)

# 主体内部的深色圆孔，应形成清晰的闭合边缘。
cv2.circle(image, (235, 205), 32, 45, -1)
cv2.circle(image, (405, 205), 22, 45, -1)

# 主体内部绘制一条较弱划痕，测试低对比度边缘能否保留。
cv2.line(image, (245, 305), (395, 305), 145, 2)

# 添加一条明显缺口，使外轮廓局部发生变化。
cv2.rectangle(image, (470, 270), (490, 315), 45, -1)

# 在背景中加入少量亮点与短纹理，作为可能的伪边缘。
for x, y in [(75, 90), (95, 330), (545, 120), (565, 350), (100, 410)]:
    cv2.circle(image, (x, y), 2, 125, -1)

for y in (155, 245, 395):
    cv2.line(image, (40, y), (115, y), 70, 1)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
saved = cv2.imwrite(str(OUTPUT_PATH), image)

if not saved:
    raise RuntimeError(f"{OUTPUT_PATH.name} 保存失败")

print(f"{OUTPUT_PATH.name} 保存成功")
