"""创建开运算与闭运算使用的标准二值测试图。"""

from pathlib import Path

import cv2
import numpy as np


DAY_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = DAY_DIR / "images" / "morphology_test.png"

# 创建 640×480 的纯黑单通道图片。
image = np.zeros((480, 640), dtype=np.uint8)

# 左侧白色主体：周围加入孤立白点和细毛刺，用于观察开运算。
cv2.rectangle(image, (80, 120), (270, 360), 255, -1)

# 白色孤立噪点：3×3 开运算后应被清除。
white_noise_points = [
    (35, 75),
    (55, 410),
    (115, 65),
    (305, 105),
    (300, 390),
]
for x, y in white_noise_points:
    cv2.circle(image, (x, y), 1, 255, -1)

# 与主体连接的细白毛刺：开运算后应缩短或消失。
cv2.line(image, (175, 120), (175, 105), 255, 1)
cv2.line(image, (270, 220), (288, 220), 255, 1)
cv2.line(image, (160, 360), (160, 377), 255, 1)

# 右侧白色主体：内部加入黑孔和细断口，用于观察闭运算。
cv2.rectangle(image, (370, 120), (560, 360), 255, -1)

# 黑色小孔：3×3 闭运算后应被填补。
black_holes = [
    (410, 170),
    (480, 225),
    (525, 315),
]
for x, y in black_holes:
    cv2.circle(image, (x, y), 1, 0, -1)

# 从右侧边缘切入的细黑断口：闭运算后应缩短或闭合。
cv2.line(image, (560, 260), (542, 260), 0, 1)

# 主体内部的细黑裂缝：闭运算后应闭合。
cv2.line(image, (445, 285), (470, 285), 0, 1)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
saved = cv2.imwrite(str(OUTPUT_PATH), image)

if not saved:
    raise RuntimeError(f"{OUTPUT_PATH.name} 保存失败")

print(f"{OUTPUT_PATH.name} 保存成功")
