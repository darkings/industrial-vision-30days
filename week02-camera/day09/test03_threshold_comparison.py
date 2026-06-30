"""
Description:
Author: Jie.Zh
Date: 2026-06-29 23:42:23
LastEditTime: 2026-06-29 23:44:44
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "step02_exposure_1000us.png"

OUTPUTS_PATH = BASE_DIR / "outputs" / "test03_threshold_comparison"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
image_name = IMAGE_FILE_PATH.stem

MULTI_THRESHOLDS = [60, 80, 100, 120, 140]
MIN_AREA = 300


# 转化为灰度图
def convert_gray_image(image):
    import cv2

    if image is None:
        raise RuntimeError("图片获取失败！")

    if image.ndim == 2:
        return image
    if image.ndim == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raise RuntimeError(f"灰度图转化失败，当前图片维度为{image.ndim}")


# 二值图
def convert_binary_image(gray, threshold):
    import cv2

    ret, binary = cv2.threshold(
        gray,
        threshold,
        255,
        cv2.THRESH_BINARY,
    )
    if ret != threshold:
        raise RuntimeError("实际阈值与固定阈值不相同")
    return binary


# 轮廓标注
def contour_annotation(contour, marked, color):
    import cv2

    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(marked, (x, y), (x + w, y + h), color, 1, cv2.LINE_AA)


# 打印阈值对应的信息
def print_threshold_stats(
    binary,
    threshold,
    valid_contours,
    original_contour_count,
):
    import cv2
    import numpy as np

    white_pixels = np.count_nonzero(binary == 255)
    white_ratio = white_pixels / binary.size * 100

    areas = sorted([cv2.contourArea(cnt) for cnt in valid_contours], reverse=True)
    max_area = areas[0] if len(areas) != 0 else "0"
    print(
        f"当前阈值：{threshold}\n"
        f"白色像素比例：{white_ratio:.2f}% "
        f"原始轮廓数量：{original_contour_count} "
        f"有效轮廓数量：{len(valid_contours)} "
        f"最大有效轮廓面积：{max_area}"
    )


# 保存图片
def saved_image(path, image):
    import cv2

    saved = cv2.imwrite(str(path), image)
    if not saved:
        raise RuntimeError(f"{path.name} 保存失败")


def main():
    import cv2

    image = cv2.imread(str(IMAGE_FILE_PATH))
    gray = convert_gray_image(image)
    # 循环固定阈值数组
    for threshold in MULTI_THRESHOLDS:
        # 复制图片
        marked_image = image.copy()
        # 保存图片路径
        binary_path = OUTPUTS_PATH / f"threshold_{threshold}_binary.png"
        result_path = OUTPUTS_PATH / f"threshold_{threshold}_contours.png"
        # 二值化图片
        binary = convert_binary_image(gray, threshold)
        # 寻找轮廓
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        valid_contours = []
        # 循环轮廓
        for contour in contours:
            area = cv2.contourArea(contour)
            # 有效轮廓
            if area >= MIN_AREA:
                valid_contours.append(contour)
                contour_annotation(contour, marked_image, (0, 255, 0))
        # 打印阈值对应信息
        print_threshold_stats(binary, threshold, valid_contours, len(contours))
        # 保存图片
        saved_image(binary_path, binary)
        saved_image(result_path, marked_image)


main()
