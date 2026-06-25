"""
Descripttion:
Author: Jie.Zh
Date: 2026-06-25 09:38:38
LastEditTime: 2026-06-25 09:46:09
"""

from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_PATH = BASE_DIR / "outputs" / "part_identification"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_path = BASE_DIR / "images" / "pipeline_test.png"
image_name = image_path.stem
marked_path = OUTPUTS_PATH / f"{image_name}_marked.png"

# 读取图片
image = cv2.imread(str(image_path))
if image is None:
    raise FileNotFoundError("图片读取失败")

# 复制图片
marked_image = image.copy()

# 灰度化
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# OTSU 二值化
used_threshold, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)

# 卷积核
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# 开运算
clean_binary_image = cv2.morphologyEx(
    binary_image,
    cv2.MORPH_OPEN,
    kernel,
)

# 查找外部轮廓
contours, _ = cv2.findContours(
    clean_binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

# 筛选面积
min_area = 500
# 有效轮廓序列
valid_contours = []
valid_index = 0
# 循环轮廓序列
for contour in contours:
    area = cv2.contourArea(contour)
    # 筛选
    if area >= min_area:
        valid_index += 1
        x, y, width, height = cv2.boundingRect(contour)
        center_x = x + width // 2
        center_y = y + height // 2
        # 在有效轮廓序列中添加当前有效轮廓的字典
        valid_contours.append(
            {
                "id": valid_index,
                "contour": contour,
                "area": area,
                "x": x,
                "y": y,
                "w": width,
                "h": height,
                "center_x": center_x,
                "center_y": center_y,
            }
        )

# 排序根据x坐标
valid_contours.sort(key=lambda parent: parent["x"])
# 标准件
standard_part = valid_contours[0]

# 排序根据y坐标，y坐标最小谁最在图片的上方
valid_contours.sort(key=lambda parent: parent["y"])

# Next() 生成器表达式
# 在结果中找到第一个满足条件的就返回
# 如果没有满足条件的就返回None
target_part = next(
    (c for c in valid_contours if c["center_x"] > image.shape[1] * 0.5),
    None,
)

# 有效循环中删除已经找到的标准件和待检测件
valid_contours = [
    c
    for c in valid_contours
    if c["id"] != standard_part["id"] and c["id"] != target_part["id"]
]

# 再根据最大面积排序
valid_contours.sort(key=lambda parent: parent["area"], reverse=True)

interference_part = valid_contours[0]

marked_parts = [
    {
        "status": "STANDARD",
        "color": (0, 255, 0),
        "part": standard_part,
    },
    {
        "status": "TARGET",
        "color": (0, 255, 255),
        "part": target_part,
    },
    {
        "status": "INTERFERENCE",
        "color": (0, 0, 255),
        "part": interference_part,
    },
]

# 循环画框和文字
for part in marked_parts:
    status = part["status"]
    color = part["color"]
    contour = part["part"]

    x1 = contour["x"]
    x2 = contour["x"] + contour["w"]
    y1 = contour["y"]
    y2 = contour["y"] + contour["h"]
    # 画框
    cv2.rectangle(
        marked_image,
        (x1, y1),
        (x2, y2),
        color,
        1,
        cv2.LINE_AA,
    )

    # 标注文字
    marked_labels = [
        f"{status}",
        f"W: {contour['w']}",
        f"H: {contour['h']}",
    ]
    label_x = x1
    label_y = max(y1 - 40, 30)
    for index, label in enumerate(marked_labels):
        cv2.putText(
            marked_image,
            label,
            (label_x, label_y + index * 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

    # 打印：
    print(
        f"当前目标身份：{status}\n"
        f"面积：{contour['area']} 尺寸：{contour['w']}x{contour['h']}"
    )

# 保存图片
saved_marked = cv2.imwrite(str(marked_path), marked_image)

if saved_marked:
    print(f"{marked_path.name} 保存成功！")
else:
    print(f"{marked_path.name} 保存失败！")
