import json

from camera_common.hik_mvs import HikCamera
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "multi_frame_stability_check"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# 函数：保存图片
def save_image(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


# 函数：预处理 灰度、高斯滤波、二值化
def preprocess_image(image):
  import cv2

  # 转灰度图
  if len(image.shape) == 2:
    gray = image.copy()
  else:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  # 高斯滤波
  blur = cv2.GaussianBlur(gray, (5, 5), 0)
  # OTSU二值化
  used_threshold, binary = cv2.threshold(
    blur,
    0,
    255,
    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU,
  )
  return used_threshold, gray, blur, binary


# 函数：找轮廓并过滤
def find_valid_contours(binary, image):
  import cv2

  image_height, image_width = image.shape[:2]
  # 找轮廓
  contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
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
  return contours, valid_contours


# 函数：画检测框
def draw_result(valid_contours, image):
  import cv2

  result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  for contour in valid_contours:
    cv2.rectangle(
      result_image,
      (contour["x"], contour["y"]),
      (contour["x"] + contour["w"], contour["y"] + contour["h"]),
      (0, 255, 0),
      1,
      cv2.LINE_AA,
    )
  return result_image


# 函数：OK/NG判定
def judge_result(valid_contours):
  if len(valid_contours) != 1:
    return "NG", "valid_contours_count != 1"
  target = valid_contours[0]
  if target["area"] > 50000 or target["area"] < 10000:
    return "NG", "area out of range"
  if target["aspect_ratio"] < 0.5 or target["aspect_ratio"] > 5:
    return "NG", "aspect_ratio out of range"
  return "OK", "target matched rules"


# 函数：
def build_frame_json(index, threshold, valid_contours):
  status, reason = judge_result(valid_contours)
  x = y = w = h = area = aspect_ratio = 0
  if status == "OK":
    target = valid_contours[0]
    x = int(target["x"])
    y = int(target["y"])
    w = int(target["w"])
    h = int(target["h"])
    area = float(target["area"])
    aspect_ratio = round(float(target["aspect_ratio"]), 3)
  return status, {
    "frame_index": index,
    "status": status,
    "reason": reason,
    "valid_contour_count": len(valid_contours),
    "x": x,
    "y": y,
    "w": w,
    "h": h,
    "area": area,
    "aspect_ratio": aspect_ratio,
    "otsu_threshold": threshold,
  }


def build_and_save_summary_json(frame_count, ok_count, frames_json):
  json_path = OUTPUTS_DIR / "summary.json"
  json_data = {
    "frame_count": frame_count,
    "ok_count": ok_count,
    "ng_count": frame_count - ok_count,
    "frames": frames_json,
  }
  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)


def main():
  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(1200)
    camera.discard_frames(5)
    frames_json = []
    total_count = 20
    ok_count = 0
    for index in range(1, total_count + 1):
      image = camera.grab_one_frame()

      used_threshold, _, _, binary = preprocess_image(image)
      _, valid_contours = find_valid_contours(binary, image)
      result = draw_result(valid_contours, image)
      status, json_data = build_frame_json(index, used_threshold, valid_contours)
      frames_json.append(json_data)
      if status == "OK":
        ok_count += 1
      result_path = OUTPUTS_DIR / f"frame_{index:02d}_result.png"
      save_image(result_path, result)
    build_and_save_summary_json(total_count, ok_count, frames_json)


if __name__ == "__main__":
  main()
