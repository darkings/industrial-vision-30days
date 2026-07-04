from __future__ import annotations


def calculate_gray_stats(image):
  """
  统计灰度或 BGR 图像的基础亮度信息。
  """

  import numpy as np

  if image.ndim == 3:
    import cv2

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  else:
    gray = image

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
