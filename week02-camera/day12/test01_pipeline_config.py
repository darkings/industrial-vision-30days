import json

from camera_common.hik_mvs import HikCamera
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "pipeline_config"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def capture_image():
  """获取图像

  Returns:
      image: 图像数组
  """
  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(1200)
    camera.discard_frames(5)
    image = camera.grab_one_frame()
  return image


def preprocess_image(image):
  """图像处理函数

  Args:
      image (ndarray): 图像数组

  Returns:
      gray:灰度图
      blur：高斯模糊图
      binary：二值图
      use_threshold:OTSU阈值
  """
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
  return gray, blur, binary, used_threshold


def find_valid_contours(binary, image):
  """寻找有效轮廓

  Args:
      binary (ndarray): 二值图
      image (ndarray): 原图

  Returns:
      contours: 所有轮廓
      valid_contours:有效轮廓
  """
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


def draw_result(image, valid_contours):
  """绘制结果图

  Args:
      image (ndarray): 原图
      valid_contours (List): 有效轮廓

  Returns:
      result_image: 绘制后的结果图
  """
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


def judge_result(valid_contours):
  """判断结果

  Args:
      valid_contours (list): 有效轮廓

  Returns:
      status: 判断结果
      reason: NG原因
  """
  if len(valid_contours) != 1:
    return "NG", "valid_contour_count != 1"
  target = valid_contours[0]
  if target["area"] > 50000 or target["area"] < 10000:
    return "NG", "area out of range"
  if target["aspect_ratio"] < 0.5 or target["aspect_ratio"] > 5:
    return "NG", "aspect_ratio out of range"
  return "OK", "target matched rules"


def build_detection_result(image, used_threshold, contours, valid_contours):
  """构建检测结果

  Args:
      image (ndarray): 原图
      used_threshold (float): OTSU阈值
      contours (List): 所有轮廓
      valid_contours (List): 有效轮廓

  Returns:
      json_data: json
  """
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


def save_image(path, image):
  """保存图片

  Args:
      path (Path): 保存图片路径
      image (ndarray): 保存图片

  Raises:
      RuntimeError: 保存失败
  """
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_outputs(image, gray, blur, binary, result, json_data):
  """保存结果

  Args:
      image (ndarray): 原图
      gray (ndarray): 灰度图
      blur (ndarray): 高斯滤波图
      binary (ndarray): 二值图
      result (ndarray): 标注结果图
      json_data (JSON): 结果JSON
  """
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


def run_detection_pipeline(image):
  """运行检测程序

  Args:
      image (ndarray): 原图

  Returns:
      gray: 灰度图
      blur：高斯滤波图
      binary：二值图
      result：标注结果图
      json_data:结果JSON
  """
  gray, blur, binary, used_threshold = preprocess_image(image)
  contours, valid_contours = find_valid_contours(binary, image)
  result = draw_result(image, valid_contours)
  json_data = build_detection_result(image, used_threshold, contours, valid_contours)
  return gray, blur, binary, result, json_data


def main():
  image = capture_image()
  gray, blur, binary, result, json_data = run_detection_pipeline(image)
  save_outputs(image, gray, blur, binary, result, json_data)


if __name__ == "__main__":
  main()
