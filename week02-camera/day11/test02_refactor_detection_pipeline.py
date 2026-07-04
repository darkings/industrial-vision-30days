import json
from pathlib import Path
from camera_common.hik_mvs import HikCamera

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "refactor_detection_pipeline"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# 函数：保存图片
def save_image(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


# 函数：抓图
def capture_image():
  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(1200)
    camera.discard_frames(5)
    image = camera.grab_one_frame()
  return image


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


# 函数：组装JSON
def build_json_result(image, used_threshold, contours, valid_contours):
  image_height, image_width = image.shape[:2]
  status, reason = judge_result(valid_contours)
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
        "aspect_ratio": round(float(item["aspect_ratio"]), 3),
      }
    )
  return json_data


def save_outputs(image, gray, blur, binary, result, json_data):
  original_path = OUTPUTS_DIR / "original.png"
  gray_path = OUTPUTS_DIR / "gray.png"
  blur_path = OUTPUTS_DIR / "blur.png"
  binary_path = OUTPUTS_DIR / "binary.png"
  result_path = OUTPUTS_DIR / "result.png"
  json_path = OUTPUTS_DIR / "detection_result.json"

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)
  if image is not None:
    save_image(original_path, image)
  if gray is not None:
    save_image(gray_path, gray)
  if blur is not None:
    save_image(blur_path, blur)
  if binary is not None:
    save_image(binary_path, binary)
  if result is not None:
    save_image(result_path, result)


# 函数：main
def main():
  image = capture_image()
  used_threshold, gray, blur, binary = preprocess_image(
    image,
  )
  contours, valid_contours = find_valid_contours(binary, image)
  result = draw_result(valid_contours, image)
  json_data = build_json_result(image, used_threshold, contours, valid_contours)
  save_outputs(image, gray, blur, binary, result, json_data)


if __name__ == "__main__":
  main()
