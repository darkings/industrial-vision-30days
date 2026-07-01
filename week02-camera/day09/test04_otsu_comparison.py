"""
Description:
Author: Jie.Zh
Date: 2026-06-30 10:12:30
LastEditTime: 2026-06-30 10:12:58
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "step02_exposure_1000us.png"

OUTPUTS_PATH = BASE_DIR / "outputs" / "test04_otsu_comparison"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
fixed_binary_path = OUTPUTS_PATH / "fixed_100_binary.png"
otsu_binary_path = OUTPUTS_PATH / "otsu_binary.png"
fixed_contours_path = OUTPUTS_PATH / "fixed_100_contours.png"
otsu_contours_path = OUTPUTS_PATH / "otsu_contours.png"

MIN_AREA = 300
FIXED_THRESHOLD = 100


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
  return ret, binary


def convert_otsu_binary_image(gray):
  import cv2

  return cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
  )


# 轮廓标注
def contour_annotation(contour, marked, color):
  import cv2

  x, y, w, h = cv2.boundingRect(contour)
  cv2.rectangle(marked, (x, y), (x + w, y + h), color, 1, cv2.LINE_AA)


# 根据轮廓获取最大面积
def get_contour_maximum_area(contours):
  import cv2

  areas = sorted([cv2.contourArea(cnt) for cnt in contours], reverse=True)

  return areas[0] if len(areas) != 0 else 0


# 保存图片
def saved_image(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"{path.name} 保存失败")


def main():
  import cv2

  # 读取图像并转灰度图
  image = cv2.imread(str(IMAGE_FILE_PATH))
  gray = convert_gray_image(image)
  marked_fixed_image = image.copy()
  marked_otsu_image = image.copy()
  # 固定/otsu 阈值 二值图
  fixed_threshold, fixed_binary = convert_binary_image(gray, FIXED_THRESHOLD)
  otsu_threshold, otsu_binary = convert_otsu_binary_image(gray)
  # 固定阈值寻找轮廓
  fixed_contours, _ = cv2.findContours(
    fixed_binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  # otsu阈值寻找轮廓
  otsu_contours, _ = cv2.findContours(
    otsu_binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  # 固定/otsu 阈值有效轮廓数量
  otsu_valid_count = 0
  fixed_valid_count = 0
  # 固定/otsu 阈值有效轮廓数组
  otsu_valid_contours = []
  fixed_valid_contours = []
  # 寻找固定阈值有效轮廓
  for contour in fixed_contours:
    area = cv2.contourArea(contour)
    if area >= MIN_AREA:
      fixed_valid_count += 1
      fixed_valid_contours.append(contour)
      contour_annotation(contour, marked_fixed_image, (0, 255, 0))
  # 寻找otsu阈值有效轮廓
  for contour in otsu_contours:
    area = cv2.contourArea(contour)
    if area >= MIN_AREA:
      otsu_valid_count += 1
      otsu_valid_contours.append(contour)
      contour_annotation(contour, marked_otsu_image, (0, 255, 0))
  # 固定/otsu 阈值最大面积
  fixed_max_area = get_contour_maximum_area(fixed_valid_contours)
  otsu_max_area = get_contour_maximum_area(otsu_valid_contours)

  # 打印
  print(
    f"固定阈值为:{fixed_threshold}\n"
    f"有效轮廓数量：{fixed_valid_count} "
    f"有效轮廓最大面积：{fixed_max_area}"
  )
  print(
    f"OTSU阈值为:{otsu_threshold}\n"
    f"有效轮廓数量：{otsu_valid_count} "
    f"有效轮廓最大面积：{otsu_max_area}"
  )
  # 保存
  saved_image(fixed_binary_path, fixed_binary)
  saved_image(otsu_binary_path, otsu_binary)
  saved_image(fixed_contours_path, marked_fixed_image)
  saved_image(otsu_contours_path, marked_otsu_image)


if (__name__) == "__main__":
  main()
