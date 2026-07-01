from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "step02_exposure_1000us.png"
OUTPUTS_PATH = BASE_DIR / "outputs" / "test06_frame_analysis_function"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

FILTER_AREA = 300


def ensure_gray_image(frame):
  if frame is None:
    raise RuntimeError("图片读取失败！")
  if frame.ndim == 2:
    return frame
  if frame.ndim == 3:
    import cv2

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame
  raise RuntimeError(f"转化灰度图失败！当前图片的维度为{frame.ndim}")


# 保存图片
def saved_image(path, image):
  import cv2
  import numpy as np

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"{path.name} 保存失败")


def analyze_frame(frame, filter_area, output_dir):
  import cv2
  import numpy as np

  gray = ensure_gray_image(frame)
  # 图片高宽
  height, width = gray.shape[:2]
  # 结果图
  marked = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
  # otsu二值化
  use_threshold, binary = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
  )
  # 开运算之前的白色像素占比
  white_pixels_before_open = np.count_nonzero(binary == 255)
  white_ratio_before_open = (white_pixels_before_open / binary.size) * 100
  # 5x5 卷积核
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
  # 开运算
  opened_image = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    kernel,
  )
  # 开运算之后的白色像素占比
  white_pixels_after_open = np.count_nonzero(opened_image == 255)
  white_ratio_after_open = (white_pixels_after_open / opened_image.size) * 100
  # 找轮廓
  contours, _ = cv2.findContours(
    opened_image,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  valid_contours = []
  # 面积过滤
  for contour in contours:
    area = cv2.contourArea(contour)
    if area >= filter_area:
      valid_contours.append(contour)
      x, y, w, h = cv2.boundingRect(contour)
      # 画有效轮廓框
      cv2.rectangle(
        marked,
        (x, y),
        (x + w, y + h),
        (0, 255, 255),
        1,
        cv2.LINE_AA,
      )
  # 最大面积排序
  areas = sorted([cv2.contourArea(cnt) for cnt in valid_contours], reverse=True)
  max_area = areas[0] if len(areas) != 0 else 0
  # 拼接路径
  gray_path = output_dir / "gray.png"
  otsu_binary_path = output_dir / "otsu_binary.png"
  otsu_open_path = output_dir / "otsu_open_5x5.png"
  result_contours_path = output_dir / "result_contours.png"

  # 保存图片
  saved_image(gray_path, gray)
  saved_image(otsu_binary_path, binary)
  saved_image(otsu_open_path, opened_image)
  saved_image(result_contours_path, marked)

  return {
    "width": width,
    "height": height,
    "otsu_threshold": use_threshold,
    "raw_contour_count": len(contours),
    "valid_contour_count": len(valid_contours),
    "max_valid_area": max_area,
    "white_ratio_before_open": white_ratio_before_open,
    "white_ratio_after_open": white_ratio_after_open,
  }


def main():
  import cv2

  frame = cv2.imread(str(IMAGE_FILE_PATH))

  stats = analyze_frame(frame, FILTER_AREA, OUTPUTS_PATH)
  print(stats)


if (__name__) == "__main__":
  main()
