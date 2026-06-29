# -- coding: utf-8 --
"""
Day 9：相机抓帧图像接入 OpenCV 检测流程，第 1 节。

本节目标：

1. 读取 Day08 真实工业相机抓到的 PNG 图像。
2. 确认图像是不是 OpenCV 可处理的 numpy.ndarray。
3. 统计灰度均值、最小值、最大值和过曝比例。
4. 生成灰度直方图。
5. 使用固定阈值做二值化。
6. 查找外部轮廓并画出轮廓框。

注意：

当前还没有稳定支架和稳定光源，所以本节只学习流程接入，
不做稳定 OK/NG 结论。
"""

from pathlib import Path


# 当前脚本所在目录：week02-camera/day09。
BASE_DIR = Path(__file__).resolve().parent

# Day08 已经验证过 ExposureTime = 1000 us 比较适合继续做阈值分割入门。
# 这里优先读取 Day08 曝光对比实验保存的 1000 us 图像。
PROJECT_DIR = BASE_DIR.parents[1]
INPUT_IMAGE_PATH = (
    PROJECT_DIR
    / "week02-camera"
    / "day08"
    / "outputs"
    / "exposure_comparison"
    / "step02_exposure_1000us.png"
)

# Day09 的输出统一保存到自己的 outputs 目录，避免和 Day08 混在一起。
OUTPUT_DIR = BASE_DIR / "outputs" / "test01_camera_image_analysis"
OUTPUT_BINARY_PATH = OUTPUT_DIR / "binary_threshold_100.png"
OUTPUT_CONTOURS_PATH = OUTPUT_DIR / "contours_threshold_100.png"
OUTPUT_HISTOGRAM_PATH = OUTPUT_DIR / "gray_histogram.png"


def ensure_gray_image(image):
    """
    确保输入图像是单通道灰度图。

    OpenCV 的 cv2.imread(path, cv2.IMREAD_UNCHANGED) 可能读到：

    - 二维数组：灰度图，shape 是 (height, width)
    - 三维数组：彩色图，shape 是 (height, width, channels)

    当前相机是 Mono8，正常应该读到二维灰度图。
    但为了让函数更通用，如果读到彩色图，就转成灰度图。
    """

    if image is None:
        raise ValueError("输入图像是 None，请先确认图片路径是否正确。")

    if image.ndim == 2:
        return image

    if image.ndim == 3:
        import cv2

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    raise ValueError(f"不支持的图像维度：image.ndim={image.ndim}")


def calculate_gray_stats(image):
    """
    统计灰度图的基础亮度信息。

    参数：
    - image：OpenCV 读到的图像，类型通常是 numpy.ndarray。

    返回：
    - width：宽度，对应 shape[1]
    - height：高度，对应 shape[0]
    - mean_gray：平均灰度，越高表示整体越亮
    - min_gray：最暗像素
    - max_gray：最亮像素
    - overexposed_pixels：灰度等于 255 的像素数量
    - overexposed_ratio：过曝比例，单位 %
    """

    import numpy as np

    gray = ensure_gray_image(image)
    height, width = gray.shape[:2]
    pixel_count = width * height
    overexposed_pixels = int(np.count_nonzero(gray == 255))

    return {
        "width": width,
        "height": height,
        "mean_gray": round(float(np.mean(gray)), 2),
        "min_gray": int(np.min(gray)),
        "max_gray": int(np.max(gray)),
        "overexposed_pixels": overexposed_pixels,
        "overexposed_ratio": round(overexposed_pixels / pixel_count * 100, 2),
    }


def apply_fixed_threshold(image, threshold_value: int):
    """
    对灰度图做固定阈值分割。

    cv2.threshold(src, thresh, maxval, type) 的核心参数：

    - src：输入灰度图。
    - thresh：阈值。大于这个值的像素会被处理成 maxval。
    - maxval：二值图中的白色值，通常是 255。
    - type：阈值类型。THRESH_BINARY 表示大于阈值变白，否则变黑。

    返回值：
    - ret：OpenCV 实际使用的阈值。固定阈值时通常等于 threshold_value。
    - binary：二值图，像素只有 0 和 255。
    """

    import cv2

    gray = ensure_gray_image(image)
    ret, binary = cv2.threshold(
        gray,
        threshold_value,
        255,
        cv2.THRESH_BINARY,
    )

    if ret != threshold_value:
        raise RuntimeError(f"阈值异常：期望 {threshold_value}，实际 {ret}")

    return binary


def find_external_contours(binary_image, min_area: float):
    """
    查找二值图中的外部轮廓，并按面积过滤小噪点。

    cv2.findContours(image, mode, method) 的核心参数：

    - image：输入二值图。
    - mode：轮廓检索模式。RETR_EXTERNAL 只找最外层轮廓。
    - method：轮廓近似方法。CHAIN_APPROX_SIMPLE 会压缩水平、垂直、斜线段。

    注意：
    findContours 会分析白色区域，因此阈值分割结果中目标通常应为白色。
    """

    import cv2

    contours, _ = cv2.findContours(
        binary_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    return [
        contour
        for contour in contours
        if cv2.contourArea(contour) >= min_area
    ]


def save_gray_histogram(gray_image, output_path: Path) -> None:
    """
    保存灰度直方图图片。

    直方图用于观察：

    - 大量像素集中在暗部还是亮部。
    - 是否有很多像素堆在 255，形成过曝。
    - 前景和背景是否有明显灰度差异。
    """

    import cv2
    import matplotlib.pyplot as plt

    gray = ensure_gray_image(gray_image)
    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])

    plt.figure(figsize=(8, 4))
    plt.plot(histogram, color="black")
    plt.title("Gray Histogram")
    plt.xlabel("Gray Value")
    plt.ylabel("Pixel Count")
    plt.xlim([0, 255])
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def draw_contour_boxes(gray_image, contours):
    """
    在图像上画出轮廓外接矩形。

    灰度图本身只有一个通道，直接画彩色框不方便。
    所以先用 cv2.cvtColor 转成 BGR 三通道图，再画绿色矩形框。
    """

    import cv2

    gray = ensure_gray_image(gray_image)
    marked = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(
            marked,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

    return marked


def main():
    """
    运行 Day09 第 1 节完整流程。
    """

    import cv2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(INPUT_IMAGE_PATH), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"读取图片失败：{INPUT_IMAGE_PATH}")

    gray = ensure_gray_image(image)
    stats = calculate_gray_stats(gray)

    binary = apply_fixed_threshold(gray, threshold_value=100)
    contours = find_external_contours(binary, min_area=100.0)
    marked = draw_contour_boxes(gray, contours)

    save_gray_histogram(gray, OUTPUT_HISTOGRAM_PATH)

    if not cv2.imwrite(str(OUTPUT_BINARY_PATH), binary):
        raise RuntimeError(f"保存二值图失败：{OUTPUT_BINARY_PATH}")

    if not cv2.imwrite(str(OUTPUT_CONTOURS_PATH), marked):
        raise RuntimeError(f"保存轮廓图失败：{OUTPUT_CONTOURS_PATH}")

    print("=== Day09 相机图像 OpenCV 分析 ===")
    print(f"输入图片：{INPUT_IMAGE_PATH}")
    print(f"图像尺寸：{stats['width']} x {stats['height']}")
    print(f"平均灰度：{stats['mean_gray']:.2f}")
    print(f"灰度范围：{stats['min_gray']} 到 {stats['max_gray']}")
    print(f"过曝比例：{stats['overexposed_ratio']:.2f}%")
    print(f"固定阈值：100")
    print(f"有效轮廓数量：{len(contours)}")
    print(f"二值图：{OUTPUT_BINARY_PATH}")
    print(f"轮廓图：{OUTPUT_CONTOURS_PATH}")
    print(f"直方图：{OUTPUT_HISTOGRAM_PATH}")


if __name__ == "__main__":
    main()
