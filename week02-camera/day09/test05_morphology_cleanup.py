"""
Description: 相机真实图片形态学处理
Author: Jie.Zh
Date: 2026-06-30 11:18:20
LastEditTime: 2026-06-30 14:16:52
"""

from pathlib import Path

from cv2 import findContours, getStructuringElement
from numpy import save

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "images" / "step02_exposure_1000us.png"

OUTPUTS_PATH = BASE_DIR / "outputs" / "test05_morphology_cleanup"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
otsu_binary_path = OUTPUTS_PATH / "otsu_binary.png"
otsu_open_path = OUTPUTS_PATH / "otsu_open_5x5.png"
otsu_close_path = OUTPUTS_PATH / "otsu_close_5x5.png"
otsu_contours_path = OUTPUTS_PATH / "otsu_contours.png"
otsu_open_contours_path = OUTPUTS_PATH / "otsu_open_contours.png"
otsu_close_contours_path = OUTPUTS_PATH / "otsu_close_contours.png"

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


# 转化otsu 二值图
def convert_otsu_binary_image(gray):
  import cv2

  return cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY | cv2.THRESH_OTSU,
  )


# 找轮廓
def getContours(binary):
  import cv2

  contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  return contours


# 绘制外接矩形
def draw_rectangle(marked, contour, color):
  import cv2

  x, y, w, h = cv2.boundingRect(contour)
  cv2.rectangle(marked, (x, y), (x + w, y + h), color, 1, cv2.LINE_AA)


# 统计 保存图片
def print_stats(image, path, contours=None, marked=None, color=None):
  import numpy as np
  import cv2

  white_pixels = np.count_nonzero(image == 255)
  white_ratio = (white_pixels / image.size) * 100

  print(f"{path.name} 图片统计：\n白色像素比例：{white_ratio:.2f}%")

  if contours is not None:
    valid_contours = []
    for contour in contours:
      area = cv2.contourArea(contour)
      if area >= MIN_AREA:
        valid_contours.append(contour)
        draw_rectangle(marked, contour, color)
    areas = sorted([cv2.contourArea(cnt) for cnt in valid_contours], reverse=True)
    max_area = areas[0] if len(valid_contours) != 0 else 0
    # 继续打印
    print(
      f"原始轮廓数量：{len(contours)} "
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

  # 读取图片
  image = cv2.imread(IMAGE_FILE_PATH)
  marked_contours_image = image.copy()
  marked_open_contours_image = image.copy()
  marked_close_contours_image = image.copy()
  # 灰度图
  gray = convert_gray_image(image)
  # otsu二值图
  ret, binary = convert_otsu_binary_image(gray)
  # 5x5卷积核
  kernel = getStructuringElement(cv2.MORPH_RECT, (5, 5))
  # 开运算
  opened_image = cv2.morphologyEx(
    binary,
    cv2.MORPH_OPEN,
    kernel,
  )
  # 闭运算
  closed_image = cv2.morphologyEx(
    binary,
    cv2.MORPH_CLOSE,
    kernel,
  )
  # 找轮廓
  binary_contours = getContours(binary)
  opened_contours = getContours(opened_image)
  closed_contours = getContours(closed_image)
  # 打印统计信息
  # print_stats(binary, otsu_binary_path)
  # print_stats(opened_image, otsu_open_path)
  # print_stats(closed_image, otsu_close_path)
  print_stats(
    binary, otsu_binary_path, binary_contours, marked_contours_image, (0, 255, 255)
  )
  print_stats(
    opened_image,
    otsu_open_contours_path,
    opened_contours,
    marked_open_contours_image,
    (0, 255, 255),
  )
  print_stats(
    closed_image,
    otsu_close_contours_path,
    closed_contours,
    marked_close_contours_image,
    (0, 255, 255),
  )

  # 保存图片
  saved_image(otsu_binary_path, binary)
  saved_image(otsu_open_path, opened_image)
  saved_image(otsu_close_path, closed_image)
  saved_image(otsu_contours_path, marked_contours_image)
  saved_image(otsu_open_contours_path, marked_open_contours_image)
  saved_image(otsu_close_contours_path, marked_close_contours_image)


if (__name__) == "__main__":
  main()
