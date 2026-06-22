"""创建 Day 4 轮廓查找与绘制练习图。"""

from pathlib import Path

import cv2
import numpy as np


DAY_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = DAY_DIR / "images" / "contour_test.png"

# 创建暗灰色彩色背景，便于后续将绿色轮廓绘制到原图上。
image = np.full((480, 640, 3), 35, dtype=np.uint8)

# 三个独立亮色目标：矩形、圆形和不规则多边形。
cv2.rectangle(image, (70, 90), (230, 250), (205, 205, 205), -1)
cv2.circle(image, (390, 170), 75, (220, 220, 220), -1)

polygon = np.array(
    [
        [300, 320],
        [390, 275],
        [505, 320],
        [475, 410],
        [335, 410],
    ],
    dtype=np.int32,
)
cv2.fillPoly(image, [polygon], (190, 190, 190))

# 在背景加入较小的亮色噪点；它们也可能被识别为独立轮廓。
noise_objects = [
    (45, 50),
    (275, 65),
    (565, 75),
    (560, 285),
    (115, 365),
    (235, 425),
]
for x, y in noise_objects:
    cv2.circle(image, (x, y), 3, (210, 210, 210), -1)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
saved = cv2.imwrite(str(OUTPUT_PATH), image)

if not saved:
    raise RuntimeError(f"{OUTPUT_PATH.name} 保存失败")

print(f"{OUTPUT_PATH.name} 保存成功")
