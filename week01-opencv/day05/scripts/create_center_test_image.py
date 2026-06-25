from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

output_path = IMAGE_DIR / "center_test.png"

# 黑色背景，白色目标。目标故意设计成“规则 + 不规则”混合，
# 方便观察外接矩形中心与轮廓重心的差异。
image = np.zeros((520, 760, 3), dtype=np.uint8)

# 规则矩形：外接矩形中心和轮廓重心基本一致
cv2.rectangle(image, (80, 80), (230, 210), (255, 255, 255), -1)

# 规则圆形：外接矩形中心和轮廓重心基本一致
cv2.circle(image, (430, 145), 70, (255, 255, 255), -1)

# L 形目标：外接矩形中心与轮廓重心会明显不同
cv2.rectangle(image, (90, 300), (260, 360), (255, 255, 255), -1)
cv2.rectangle(image, (90, 300), (150, 470), (255, 255, 255), -1)

# 带缺口的不规则目标：中心也会偏移
pts = np.array(
    [
        [400, 300],
        [610, 300],
        [610, 455],
        [520, 455],
        [520, 380],
        [400, 380],
    ],
    dtype=np.int32,
)
cv2.fillPoly(image, [pts], (255, 255, 255))

# 小噪点：用于练习面积过滤
cv2.circle(image, (690, 80), 8, (255, 255, 255), -1)
cv2.rectangle(image, (660, 230), (680, 245), (255, 255, 255), -1)
cv2.circle(image, (310, 440), 5, (255, 255, 255), -1)

saved = cv2.imwrite(str(output_path), image)

if saved:
    print(f"{output_path.name} 保存成功！")
else:
    print(f"{output_path.name} 保存失败")
