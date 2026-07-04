import json
from pathlib import Path

from camera_common.hik_mvs import HikCamera


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "basic_detection_pipeline"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
original_path = OUTPUTS_DIR / "original.png"
gray_path = OUTPUTS_DIR / "gray.png"
blur_path = OUTPUTS_DIR / "blur.png"
binary_path = OUTPUTS_DIR / "binary.png"
result_path = OUTPUTS_DIR / "result.png"
json_path = OUTPUTS_DIR / "detection_result.json"


def saved(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def judge_result(valid_contours):
  if len(valid_contours) != 1:
    return "NG", "valid_contours_count != 1"
  target = valid_contours[0]
  if target["area"] > 50000 or target["area"] < 10000:
    return "NG", "area out of range"
  if target["aspect_ratio"] < 0.5 or target["aspect_ratio"] > 5:
    return "NG", "aspect_ratio out of range"
  return "OK", "target matched rules"


def main():
  import cv2

  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(1200)
    camera.discard_frames(5)
    image = camera.grab_one_frame()
    saved(original_path, image)
  # 图片宽高
  image_height, image_width = image.shape[:2]
  # 转灰度图
  if len(image.shape) == 2:
    gray = image.copy()
  else:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  saved(gray_path, gray)
  # 高斯滤波
  blur = cv2.GaussianBlur(gray, (5, 5), 0)
  saved(blur_path, blur)
  # OTSU二值化
  used_threshold, binary = cv2.threshold(
    blur,
    0,
    255,
    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU,
  )
  saved(binary_path, binary)
  # 找轮廓
  contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  # 标记图
  result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  # 有效轮廓数组
  valid_contours = []
  # 贴边轮廓margin
  margin = 30
  # 循环筛选有效轮廓
  for contour in contours:
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / h
    # 按面积过滤
    if area <= 1000:
      continue
    # 按外接间距过滤
    if x < margin:
      continue
    if y < margin:
      continue
    if x + w > image_width - margin:
      continue
    if y + h > image_height - margin:
      continue
    # 按宽高比过滤
    if aspect_ratio < 0.5 or aspect_ratio > 5.0:
      continue
    cv2.rectangle(
      result,
      (x, y),
      (x + w, y + h),
      (0, 255, 0),
      1,
      cv2.LINE_AA,
    )
    valid_contours.append(
      {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "area": area,
        "aspect_ratio": aspect_ratio,
        "contour": contour,
      }
    )
    print(f"有效轮廓\nw:{w} h:{h} x:{x} y:{y} area:{area} aspect_ratio:{aspect_ratio}")
  # 保存结果图
  saved(result_path, result)
  # 按面积最大排序
  valid_contours.sort(key=lambda item: item["area"], reverse=True)
  max_area = valid_contours[0]["area"] if valid_contours else 0
  # 打印OTSU阈值 轮廓数量 最大轮廓面积
  print(
    f"OTSU阈值为：{used_threshold} 原始轮廓数量为：{len(contours)} 有效轮廓数量为：{len(valid_contours)} 最大有效轮廓面积：{max_area}"
  )
  status, reason = judge_result(valid_contours)
  # 写入JSON
  json_data = {
    "image_width": image_width,
    "image_height": image_height,
    "otsu_threshold": float(used_threshold),
    "raw_contour_count": len(contours),
    "valid_contour_count": len(valid_contours),
    "status": status,
    "reason": reason,
    "objects": [],
  }

  for index, item in enumerate(valid_contours, start=1):
    json_data["objects"].append(
      {
        "index": index,
        "x": int(item["x"]),
        "y": int(item["y"]),
        "w": int(item["w"]),
        "h": int(item["h"]),
        "area": float(item["area"]),
        "aspect_ratio": float(item["aspect_ratio"]),
      }
    )

  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

  print(f"JSON保存路径：{json_path}")


if __name__ == "__main__":
  main()
