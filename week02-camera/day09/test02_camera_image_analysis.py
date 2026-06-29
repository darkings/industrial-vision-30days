from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "step02_exposure_1000us.png"

OUTPUTS_PATH = BASE_DIR / "outputs" / "test02"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
image_name = IMAGE_FILE_PATH.stem
histogram_path = OUTPUTS_PATH / f"{image_name}_histogram.png"
binary_path = OUTPUTS_PATH / f"{image_name}_binary.png"
result_path = OUTPUTS_PATH / f"{image_name}_result.png"


# 判断输入图像是灰度图
def ensure_gray_image(image):
    if image is None:
        raise FileNotFoundError("图片加载失败！")
    if image.ndim == 2:
        return image
    if image.ndim == 3:
        import cv2

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raise ValueError(f"当前图片维度为{image.ndim} 无法使用")


# 统计图像亮度信息
def calculate_gray_stats(image):
    import numpy as np

    # 统计过曝像素数量
    overexposed_count = np.count_nonzero(image == 255)
    # 过曝占比
    overexposed_ratio = overexposed_count / image.size
    height, width = image.shape[:2]
    return {
        "width": width,
        "height": height,
        "mean": np.mean(image),
        "min": np.min(image),
        "max": np.max(image),
        "overexposed": overexposed_ratio,
    }


# 固定阈值二值化
def apply_fixed_threshold(ret, image):
    import cv2

    used_threshold, binary_image = cv2.threshold(
        image,
        ret,
        255,
        cv2.THRESH_BINARY,
    )
    if used_threshold != ret:
        raise RuntimeError(f"阈值异常：期望阈值{ret} 实际阈值{used_threshold}")
    return binary_image


# 开运算后再查找轮廓
def find_external_contours(binary_image):
    import cv2

    # clean_binary_image = cv2.GaussianBlur(image, (5, 5), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    clean_binary_image = cv2.morphologyEx(
        binary_image,
        cv2.MORPH_OPEN,
        kernel,
    )
    contours, _ = cv2.findContours(
        clean_binary_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    return contours


# 保存灰度直方图
def save_gray_histogram(image):
    import cv2
    from matplotlib import pyplot as plt

    histogram = cv2.calcHist([ensure_gray_image(image)], [0], None, [256], [0, 256])
    # 绘制直方图
    plt.figure(figsize=(12, 6))
    plt.plot(histogram, color="blue", label="gray histogram")
    plt.title("gray histogram ")
    plt.xlabel("gray value")
    plt.ylabel("pixel count")
    plt.xlim([0, 255])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(str(histogram_path))
    if not histogram_path.exists():
        raise FileNotFoundError("直方图保存失败！")
    plt.close()


# 绘制外轮廓矩形
def draw_contour_boxes(contour, image, color):
    import cv2

    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(
        image,
        (x, y),
        (x + w, y + h),
        color,
        1,
        cv2.LINE_AA,
    )


# 保存图片
def saved_image(path, image):
    import cv2

    saved = cv2.imwrite(str(path), image)
    if not saved:
        raise RuntimeError(f"{path.name} 保存失败")


# 完整流程
def main():
    import cv2

    # 读取图片
    image = cv2.imread(str(IMAGE_FILE_PATH))

    # 转为灰度图
    gray_image = ensure_gray_image(image)

    marked_image = image.copy()
    # 灰度图统计
    gray_stats = calculate_gray_stats(gray_image)
    # 打印
    print(
        f"{IMAGE_FILE_PATH.name}\n"
        f"宽：{gray_stats['width']} 高：{gray_stats['height']} "
        f"平均值：{gray_stats['mean']:.2f} 最大：{gray_stats['max']:.2f} "
        f"最小：{gray_stats['min']:.2f} 过曝比例：{gray_stats['overexposed']:.3f} "
    )
    # 二值化
    binary_image = apply_fixed_threshold(100, gray_image)
    # 直方图
    save_gray_histogram(image)
    # 轮廓
    contours = find_external_contours(binary_image)
    min_area = 300
    valid_index = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            valid_index += 1
            draw_contour_boxes(contour, marked_image, (0, 255, 0))

    print(f"有效轮廓为{valid_index}条")
    # 保存图片
    saved_image(binary_path, binary_image)
    saved_image(result_path, marked_image)


main()
