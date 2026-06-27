from pathlib import Path

import cv2

# 文件夹路径
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_PATH = BASE_DIR / "outputs" / "detection_report"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# 文件路径
image_path = BASE_DIR / "images" / "pipeline_test.png"
image_name = image_path.stem
gray_path = OUTPUTS_PATH / f"{image_name}_gray.png"
binary_path = OUTPUTS_PATH / f"{image_name}_binary.png"
clean_binary_path = OUTPUTS_PATH / f"{image_name}_clean_binary.png"
marked_path = OUTPUTS_PATH / f"{image_name}_report.png"

# 读取图片
image = cv2.imread(str(image_path))
if image is None:
    raise FileNotFoundError(f"{image_path.name} 图片读取失败")
# 标注图片
marked_image = image.copy()
# 灰度化
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 二值化
_, binary_image = cv2.threshold(
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
# 寻找轮廓
contours, _ = cv2.findContours(
    clean_binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)
# 用于筛选的最小面积
min_area = 500
# 已筛选的序列
parts = []
valid_index = 0
# 循环筛选
for contour in contours:
    area = cv2.contourArea(contour)
    if area >= min_area:
        valid_index += 1
        x1, y1, w, h = cv2.boundingRect(contour)
        center_x = x1 + w // 2
        center_y = y1 + h // 2
        x2 = x1 + w
        y2 = y1 + h
        parts.append(
            {
                "id": valid_index,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "w": w,
                "h": h,
                "area": area,
                "center_x": center_x,
                "center_y": center_y,
                "contour": contour,
            }
        )

# STANDARD工件
parts.sort(key=lambda parent: parent["x1"])
standard_part = parts[0]

# TARGET工件
parts.sort(key=lambda parent: parent["y1"])
target_part = next(
    (c for c in parts if c["center_x"] > image.shape[1] * 0.5),
    None,
)

# INTERFERENCE工件
parts = [
    c for c in parts if c["id"] != standard_part["id"] and c["id"] != target_part["id"]
]
parts.sort(key=lambda parent: parent["area"], reverse=True)
interference_part = parts[0]

# 标注标准件
cv2.rectangle(
    marked_image,
    (standard_part["x1"], standard_part["y1"]),
    (standard_part["x2"], standard_part["y2"]),
    (0, 255, 0),
    1,
    cv2.LINE_AA,
)
cv2.putText(
    marked_image,
    "STANDARD",
    (standard_part["x1"], max(standard_part["y1"] + 15, 30)),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 255, 0),
    1,
    cv2.LINE_AA,
)
# 标注INTERFERENCE工件
cv2.rectangle(
    marked_image,
    (interference_part["x1"], interference_part["y1"]),
    (interference_part["x2"], interference_part["y2"]),
    (0, 0, 255),
    1,
    cv2.LINE_AA,
)
cv2.putText(
    marked_image,
    "INTERFERENCE",
    (interference_part["x1"], max(interference_part["y1"] + 15, 30)),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 0, 255),
    1,
    cv2.LINE_AA,
)
# 已知标准件宽度为50mm
standard_width_mm = 50
# 计算简单比例尺
mm_per_pixel = standard_width_mm / standard_part["w"]

# 计算待测件
target_width_mm = target_part["w"] * mm_per_pixel
target_height_mm = target_part["h"] * mm_per_pixel

# 判断待测件是否OK
width_ok = False
height_ok = False
status = ""
ng_reasons = []
if 60.0 >= target_width_mm >= 58.0:
    width_ok = True
if 40.0 >= target_height_mm >= 38.0:
    height_ok = True

if width_ok and height_ok:
    status = "OK"
else:
    status = "NG"
    ng_reasons.append("W_NG") if width_ok is False else ""
    ng_reasons.append("H_NG") if height_ok is False else ""

# 标注待检测件
cv2.rectangle(
    marked_image,
    (target_part["x1"], target_part["y1"]),
    (target_part["x2"], target_part["y2"]),
    (0, 255, 255),
    1,
    cv2.LINE_AA,
)
target_label_texts = [
    "TARGET",
    f"W:{target_width_mm:.2f}mm",
    f"H:{target_height_mm:.2f}mm",
    f"Status:{status}",
    f"{' '.join(ng_reasons)}",
]
for index, text in enumerate(target_label_texts):
    text_x = target_part["x1"]
    text_y = max(target_part["y1"] + 15, 30)
    cv2.putText(
        marked_image,
        text,
        (text_x, text_y + index * 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 255),
        1,
        cv2.LINE_AA,
    )
    print(text)

# Result背景
cv2.rectangle(
    marked_image,
    (0, 0),
    (image.shape[1], 40),
    (30, 30, 30),
    -1,
)
# Result文本
result_text = f"RESULT: {status} | SCALE: {mm_per_pixel:.4f} | TARGET W: {target_width_mm:.2f}mm | TARGET H: {target_height_mm:.2f}mm"
if status == "NG":
    result_text += " | REASON: "
    result_text += "" if width_ok else "WIDTH_NG"
    result_text += "" if height_ok else "HEIGHT_NG"

# 标注文字
cv2.putText(
    marked_image,
    result_text,
    (5, 25),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (0, 255, 0) if status == "OK" else (0, 0, 255),
    1,
    cv2.LINE_AA,
)

# 保存图片
saved_gray = cv2.imwrite(str(gray_path), gray_image)
saved_binary = cv2.imwrite(str(binary_path), binary_image)
saved_clean_binary = cv2.imwrite(str(clean_binary_path), clean_binary_image)
saved_marked = cv2.imwrite(str(marked_path), marked_image)

saved_results = [
    (saved_gray, gray_path),
    (saved_binary, binary_path),
    (saved_clean_binary, clean_binary_path),
    (saved_marked, marked_path),
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败！")
