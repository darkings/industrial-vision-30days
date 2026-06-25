from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_PATH = BASE_DIR / "outputs" / "pipeline_preview"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_path = BASE_DIR / "images" / "pipeline_test.png"
image_name = image_path.stem
gray_path = OUTPUTS_PATH / f"{image_name}_gray.png"
binary_path = OUTPUTS_PATH / f"{image_name}_binary.png"
clean_binary_path = OUTPUTS_PATH / f"{image_name}_clean_binary.png"
marked_path = OUTPUTS_PATH / f"{image_name}_marked.png"

# 读取图片
image = cv2.imread(str(image_path))
if image is None:
    raise FileNotFoundError(f"{image_path.name} 图片读取失败！")

# 复制图片
marked_image = image.copy()

# 灰度图
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

# 最小面积
min_area = 400
# 有效轮廓索引
valid_count = 0

# 循环筛选有效轮廓
for contour in contours:
    # 轮廓面积
    area = cv2.contourArea(contour)
    # 筛选有效轮廓
    if area >= min_area:
        valid_count += 1
        x, y, width, height = cv2.boundingRect(contour)
        # 绘制有效轮廓的水平外接矩形
        cv2.rectangle(
            marked_image,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

# 打印
print(
    f"OTSU 阈值：{used_threshold}\n"
    f"全部轮廓数量：{len(contours)}\n"
    f"有效轮廓数量：{valid_count}"
)

# 保存
saved_gray = cv2.imwrite(str(gray_path), gray_image)
saved_binary = cv2.imwrite(str(binary_path), binary_image)
saved_clean_binary = cv2.imwrite(str(clean_binary_path), clean_binary_image)
saved_marked = cv2.imwrite(str(marked_path), marked_image)

saved_results = [
    [saved_gray, gray_path],
    [saved_binary, binary_path],
    [saved_clean_binary, clean_binary_path],
    [saved_marked, marked_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败")
