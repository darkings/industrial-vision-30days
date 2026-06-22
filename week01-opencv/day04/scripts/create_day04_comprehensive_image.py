"""创建 Day 4 边缘、轮廓与外接矩形综合练习图。"""

from pathlib import Path

import cv2
import numpy as np


DAY_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = DAY_DIR / "images" / "day04_comprehensive_test.png"

# 使用深灰色彩色背景，方便最后绘制不同颜色的检测结果。
image = np.full((520, 760, 3), 35, dtype=np.uint8)

# 两个尺寸接近的合格矩形目标。
cv2.rectangle(image, (70, 90), (220, 230), (205, 205, 205), -1)
cv2.rectangle(image, (295, 85), (450, 230), (215, 215, 215), -1)

# 一个尺寸明显偏小的矩形目标，用于模拟尺寸异常。
cv2.rectangle(image, (555, 115), (650, 205), (200, 200, 200), -1)

# 一个细长亮色干扰物：面积可能不算很小，但长宽比明显异常。
cv2.rectangle(image, (95, 345), (350, 370), (195, 195, 195), -1)

# 一个较大的不规则目标，用于观察水平外接矩形包含背景。
polygon = np.array(
    [
        [480, 315],
        [590, 275],
        [690, 345],
        [650, 455],
        [510, 445],
    ],
    dtype=np.int32,
)
cv2.fillPoly(image, [polygon], (210, 210, 210))

# 加入小型亮色噪点，应通过面积阈值过滤。
for x, y in [(35, 40), (260, 300), (710, 70), (420, 470), (720, 485)]:
    cv2.circle(image, (x, y), 3, (220, 220, 220), -1)

# 为背景加入轻微噪声，使输入图更接近实际采集结果。
rng = np.random.default_rng(41)
noise = rng.normal(0, 3, image.shape[:2]).astype(np.int16)
for channel in range(3):
    channel_data = image[:, :, channel].astype(np.int16) + noise
    image[:, :, channel] = np.clip(channel_data, 0, 255).astype(np.uint8)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
saved = cv2.imwrite(str(OUTPUT_PATH), image)

if not saved:
    raise RuntimeError(f"{OUTPUT_PATH.name} 保存失败")

print(f"{OUTPUT_PATH.name} 保存成功")
