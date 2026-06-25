from pathlib import Path

import cv2

# 路径
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "center_test.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "contour_center"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

image_name = IMAGE_FILE_PATH.stem
original_path = OUTPUTS_PATH / f"{image_name}_original.png"
result_path = OUTPUTS_PATH / f"{image_name}_result.png"

# 读取图片并复制
image = cv2.imread(str(IMAGE_FILE_PATH))
if image is None:
    raise FileNotFoundError("图片加载失败！")
marked_image = image.copy()

# 灰度图
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 二值化
used_threshold, binary_image = cv2.threshold(
    gray_image,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
)
print(f"OTSU 自动阈值：{used_threshold}")

# 外部轮廓
contours, hierarchy = cv2.findContours(
    binary_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

valid_index = 0
min_area = 1000
print(f"面积大于等于{min_area}像素的轮廓为有效轮廓：")
# 循环轮廓序列
for contour in contours:
    # 当前轮廓面积
    area = cv2.contourArea(contour)
    # 筛选有效轮廓
    if area >= min_area:
        # 有效索引+1
        valid_index += 1
        # 周长
        perimeter = cv2.arcLength(contour, True)
        # 外接矩形 左上角 x y ，长 宽
        x, y, width, height = cv2.boundingRect(contour)
        # 长宽比
        aspect_ratio = round(width / height, 2)
        # 外接矩形中心坐标
        bounding_center_x = x + (width // 2)
        bounding_center_y = y + (height // 2)

        # 获取图像矩
        M = cv2.moments(contour)
        # 轮廓中心坐标
        if M["m00"] == 0:
            continue
        moments_center_x = int(M["m10"] / M["m00"])
        moments_center_y = int(M["m01"] / M["m00"])
        # 打印
        print(
            f"第{valid_index}条有效轮廓 "
            f"外接矩形：尺寸{width}x{height} 长宽比{aspect_ratio} 周长{perimeter} "
            f"外接矩形中心坐标：({bounding_center_x},{bounding_center_y})"
            f"轮廓重心坐标：({moments_center_x},{moments_center_y})"
        )
        # 外接矩形框
        cv2.rectangle(
            marked_image,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
        # 外接矩形中心画圆
        cv2.circle(
            marked_image,
            (bounding_center_x, bounding_center_y),
            2,
            (255, 0, 0),
            -1,
        )
        # 轮廓重心画圆
        cv2.circle(
            marked_image,
            (moments_center_x, moments_center_y),
            2,
            (0, 0, 255),
            -1,
        )

# 保存
saved_original = cv2.imwrite(str(original_path), image)
saved_result = cv2.imwrite(str(result_path), marked_image)

saved_results = [
    [saved_original, original_path],
    [saved_result, result_path],
]

for saved, path in saved_results:
    if saved:
        print(f"{path.name} 保存成功！")
    else:
        print(f"{path.name} 保存失败")
