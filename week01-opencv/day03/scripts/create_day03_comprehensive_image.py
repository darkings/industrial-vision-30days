"""创建 Day 3 阈值分割与形态学综合练习图。"""

from pathlib import Path

import cv2
import numpy as np


DAY_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = DAY_DIR / "images" / "day03_comprehensive_test.png"

height = 480
width = 640

# 创建从左到右略微变亮的灰度背景，模拟不完全均匀的工业现场光照。
background_line = np.linspace(35, 75, width, dtype=np.float32)
image = np.tile(background_line, (height, 1))

# 加入少量可重复的传感器噪声，让输入图更接近真实灰度图。
rng = np.random.default_rng(30)
noise = rng.normal(0, 4, (height, width))
image = np.clip(image + noise, 0, 255).astype(np.uint8)

# 绘制一个亮色工业零件主体。
cv2.rectangle(image, (170, 110), (470, 370), 205, -1)
cv2.rectangle(image, (260, 70), (380, 110), 205, -1)

# 在主体上制造细小白色毛刺。
cv2.line(image, (170, 185), (150, 185), 205, 1)
cv2.line(image, (470, 245), (492, 245), 205, 1)
cv2.line(image, (320, 370), (320, 392), 205, 1)

# 在背景中制造亮色孤立噪点。
white_noise_points = [
    (90, 85),
    (120, 300),
    (520, 95),
    (545, 330),
    (570, 405),
    (105, 410),
]
for x, y in white_noise_points:
    cv2.circle(image, (x, y), 1, 215, -1)

# 在白色主体内部制造黑色小孔。
black_holes = [
    (225, 175),
    (410, 320),
    (365, 205),
]
for x, y in black_holes:
    cv2.circle(image, (x, y), 1, 45, -1)

# 制造一条细小内部裂缝和一处从边缘切入的断口。
cv2.line(image, (290, 285), (315, 285), 45, 1)
cv2.line(image, (470, 300), (448, 300), 45, 1)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
saved = cv2.imwrite(str(OUTPUT_PATH), image)

if not saved:
    raise RuntimeError(f"{OUTPUT_PATH.name} 保存失败")

print(f"{OUTPUT_PATH.name} 保存成功")
