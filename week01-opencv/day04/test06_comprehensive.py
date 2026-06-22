from pathlib import Path

import cv2

# 路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "day04_comprehensive_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "comprehensive"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
gray_path = OUTPUTS_PATH / f"{image_name[:-4]}gray.png"
edges_path = OUTPUTS_PATH / f"{image_name[:-4]}edges.png"
binary_path = OUTPUTS_PATH / f"{image_name[:-4]}binary.png"
result_path = OUTPUTS_PATH / f"{image_name[:-4]}result.png"

# 读取图片
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片读取失败")
# 转为灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 灰度图高斯滤波
gaussian_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

# 高斯滤波后Canny
edge_image = cv2.Canny(gaussian_image, 50, 150)

# 灰度图 OTSU 二值图
used_threshold, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)
marked_image = image.copy()
# 找所有轮廓
contours, hierarchy = cv2.findContours(
    binary_image,  # 输入OTSU二值图
    cv2.RETR_EXTERNAL,  # 只找外轮廓
    cv2.CHAIN_APPROX_SIMPLE,  # 忽略冗余坐标
)

noise_count = 0
ok_count = 0
ng_count = 0
interference_count = 0
target_count = 0


# 循环所有轮廓
for contour in contours:
    # 获取轮廓面积
    area = cv2.contourArea(contour)
    x, y, width, height = cv2.boundingRect(contour)
    aspect_ratio = width / height
    perimeter = cv2.arcLength(contour, True)
    print(
        f"当前轮廓 面积：{area:.2f} 周长：{perimeter:.2f} 尺寸：{width}x{height} 长宽比：{aspect_ratio:.2f}"
    )
    status = ""
    target_id = ""
    color = ()

    if area < 100:
        noise_count += 1
        continue

    # 判断轮廓内面积大于100 获取所有待标注的轮廓
    if 18000 <= area <= 24000 and 0.9 <= aspect_ratio <= 1.2:
        target_count += 1
        ok_count += 1
        status = "OK"
        color = (0, 255, 0)
        target_id = f"ID:{target_count} "
    elif aspect_ratio > 3:
        interference_count += 1
        status = "INTERFERENCE"
        color = (0, 255, 255)
    else:
        target_count += 1
        ng_count += 1
        status = "NG"
        color = (0, 0, 255)
        target_id = f"ID:{target_count} "

    cv2.rectangle(
        marked_image,
        (x, y),
        (x + width, y + height),
        color,
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        marked_image,
        (f"{target_id}{status}  A:{area:.0f} AR:{aspect_ratio:.2f}"),
        (x, max(y - 10, 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
        cv2.LINE_AA,
    )


print(
    f"全部轮廓：{len(contours)}  噪点：{noise_count} 检测物：{target_count} 干扰物：{interference_count}  OK:{ok_count} NG:{ng_count}"
)
# 保存文件
saved_gray = cv2.imwrite(str(gray_path), gray_image)
saved_edges = cv2.imwrite(str(edges_path), edge_image)
saved_binary = cv2.imwrite(str(binary_path), binary_image)
saved_result = cv2.imwrite(str(result_path), marked_image)

saved_results = [
    [saved_gray, gray_path],
    [saved_edges, edges_path],
    [saved_binary, binary_path],
    [saved_result, result_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功")
    else:
        print(f"{path.name} 保存失败")
