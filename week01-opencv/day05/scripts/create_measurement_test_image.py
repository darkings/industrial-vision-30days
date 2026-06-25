from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

output_path = IMAGE_DIR / "measurement_test.png"

image = np.zeros((420, 760, 3), dtype=np.uint8)

# 左侧标准件：真实宽度假设为 50 mm，图像宽度为 250 px
cv2.rectangle(image, (80, 140), (330, 250), (255, 255, 255), -1)

# 右侧待测件：用标准件计算出的 mm_per_pixel 换算它的像素宽高
cv2.rectangle(image, (450, 120), (630, 280), (255, 255, 255), -1)

# 两个小噪点，用于练习面积过滤
cv2.circle(image, (690, 70), 7, (255, 255, 255), -1)
cv2.rectangle(image, (390, 330), (410, 345), (255, 255, 255), -1)

# 轻微参考线：不参与检测，只帮助肉眼理解左右目标
cv2.putText(
    image,
    "standard",
    (105, 125),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (120, 120, 120),
    2,
    cv2.LINE_AA,
)
cv2.putText(
    image,
    "target",
    (495, 105),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (120, 120, 120),
    2,
    cv2.LINE_AA,
)

saved = cv2.imwrite(str(output_path), image)

if saved:
    print(f"{output_path.name} 保存成功！")
else:
    print(f"{output_path.name} 保存失败")
