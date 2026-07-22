from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def read_local_image(path):
  """
  读取本地图片路径
  """
  import cv2

  validation_suffixes = [".jpg", ".png"]
  if not path.exists():
    raise RuntimeError(f"文件路径不存在:{path}")
  if path.suffix.lower() not in validation_suffixes:
    raise RuntimeError("当前读取的文件不是指定图片文件")

  image = cv2.imread(str(path))
  if image is None:
    raise RuntimeError("图片读取失败")
  return image


def convert_to_grayscale(image):
  """
  转化灰度图
  """
  import cv2

  if len(image.shape) == 3:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  return image


def convert_to_coordinates(bbox):
  """
  将x y w h 转换为x1 y1 x2 y2
  """
  x, y, w, h = bbox.values()
  x1 = x
  y1 = y
  x2 = x + w
  y2 = y + h
  return x1, y1, x2, y2


def is_in_critical_roi(critical_roi, roi_bbox):
  """
  判断是否在关键区域内
  """
  critical_x1, critical_y1, critical_x2, critical_y2 = critical_roi.values()
  roi_x1, roi_y1, roi_x2, roi_y2 = convert_to_coordinates(roi_bbox)
  x_overlap = max(critical_x1, roi_x1) < min(critical_x2, roi_x2)
  y_overlap = max(critical_y1, roi_y1) < min(critical_y2, roi_y2)
  return x_overlap and y_overlap


def find_candidate_defect_contours(gray, min_area, max_area, critical_roi):
  """
  查找候选缺陷轮廓
  """
  import cv2

  if gray is None:
    raise RuntimeError("输入图片为空")
  if min_area == 0 or min_area is None:
    raise RuntimeError("筛选条件：最小区域不能为0或为空")
  if max_area is None:
    raise RuntimeError("筛选条件：最大区域不能为空")
  contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  valid_contours = []
  valid_count = 0
  for cnt in contours:
    area = cv2.contourArea(cnt)
    if min_area <= area < max_area:
      valid_count += 1
      x, y, w, h = cv2.boundingRect(cnt)
      cnt_dict = {
        "id": valid_count,
        "bbox": {"x": x, "y": y, "width": w, "height": h},
        "area_px": area,
      }
      in_critical_roi = is_in_critical_roi(critical_roi, cnt_dict["bbox"])
      cnt_dict["region"] = "critical" if in_critical_roi else "normal"
      valid_contours.append(cnt_dict)

  return valid_contours


def judge_ok_ng(candidate_contours, max_defect_count):
  """
  判断OK还是NG
  """
  critical_defect_count = sum(
    [1 for cnt in candidate_contours if cnt["region"] == "critical"]
  )

  candidate_contour_count = len(candidate_contours)
  status, reasons = "OK", []
  if candidate_contour_count > max_defect_count:
    status = "NG"
    reasons.append(f"detected {candidate_contour_count} valid defects")

  if critical_defect_count > 0:
    status = "NG"
    reasons.append("defects are located in the critical region")

  return status, reasons


def draw_defect_annotation_image(
  candidate_defects, critical_roi, status, reasons, image
):
  """
  绘制缺陷标注图片
  """
  import cv2

  if len(image.shape) == 2:
    result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  else:
    result_image = image.copy()
  _, image_width = image.shape[:2]

  # 绘制OK/NG 原因
  status_reason_background_height = 30 if status == "OK" else len(reasons) * 40 + 30
  status_color = (0, 255, 0) if status == "OK" else (0, 0, 255)
  cv2.rectangle(
    result_image,
    (0, 0),
    (image_width, status_reason_background_height),
    (64, 64, 64),
    -1,
    cv2.LINE_AA,
  )
  cv2.putText(
    result_image,
    f"Status:{status}",
    (5, 20),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    status_color,
    1,
    cv2.LINE_AA,
  )
  if len(reasons) > 0:
    cv2.putText(
      result_image,
      "Reason:",
      (5, 40),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.5,
      status_color,
      1,
      cv2.LINE_AA,
    )
  for index, reason in enumerate(reasons):
    cv2.putText(
      result_image,
      reason,
      (5, 40 + ((index + 1) * 20)),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.5,
      status_color,
      1,
      cv2.LINE_AA,
    )

  # 绘制关键区域
  critical_color = (0, 255, 255)
  cv2.rectangle(
    result_image,
    (critical_roi["x1"], critical_roi["y1"]),
    (critical_roi["x2"], critical_roi["y2"]),
    critical_color,
    1,
    cv2.LINE_AA,
  )
  cv2.putText(
    result_image,
    "critical",
    (critical_roi["x1"] - 5, max(critical_roi["y1"] - 10, 30)),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    critical_color,
    1,
    cv2.LINE_AA,
  )

  # 绘制有效缺陷区域
  defect_color = (0, 0, 255)
  for defect in candidate_defects:
    defect_bbox = defect["bbox"]
    defect_x, defect_y, defect_w, defect_h = defect_bbox.values()
    cv2.rectangle(
      result_image,
      (defect_x, defect_y),
      (defect_x + defect_w, defect_y + defect_h),
      defect_color,
      1,
      cv2.LINE_AA,
    )
    cv2.putText(
      result_image,
      f"Defect :{defect['id']}",
      (defect_x, max(defect_y - 30, 30)),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.4,
      defect_color,
      1,
      cv2.LINE_AA,
    )
    cv2.putText(
      result_image,
      f"area_px:{defect['area_px']} region:{defect['region']}",
      (defect_x, max(defect_y - 10, 30)),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.4,
      defect_color,
      1,
      cv2.LINE_AA,
    )
  return result_image


def build_result_json(
  input_image_path,
  min_area,
  max_area,
  max_defect_count,
  binary_threshold,
  defects,
  status,
  reasons,
):
  """
  构建结构JSON
  """
  return {
    "input_image": str(input_image_path),
    "parameters": {
      "min_area": min_area,
      "max_area": max_area,
      "max_defect_count": max_defect_count,
      "binary_threshold": binary_threshold,
    },
    "defect_count": len(defects),
    "defects": defects,
    "result": status,
    "reasons": reasons,
  }


def convert_to_binary_image(gray_image, threshold):
  """
  转化为二值图
  """
  import cv2

  return cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY_INV)


def save_image(path, image):
  """
  保存单张图片
  """
  import cv2

  if image is None:
    raise RuntimeError(f"保存的图片为空：{path}")
  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_json(json_path, json_data):
  """保存JSON文件"""
  import json

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)


def save_outputs(outputs_dir, result_image, binary_image, result_json):
  """
  在输出目录保存文件
  """
  outputs_dir.mkdir(parents=True, exist_ok=True)
  binary_image_path = outputs_dir / "binary.png"
  result_image_path = outputs_dir / "result.png"
  result_json_path = outputs_dir / "result.json"
  save_image(binary_image_path, binary_image)
  save_image(result_image_path, result_image)
  save_json(result_json_path, result_json)


def main():
  inputs_dir = BASE_DIR / "inputs"
  outputs_dir = BASE_DIR / "outputs" / "defect_rules"
  image_file_path = inputs_dir / "scratches.png"

  min_area = 400
  max_area = 100000
  max_defect_count = 2
  binary_threshold = 130
  critical_roi = {"x1": 50, "y1": 200, "x2": 450, "y2": 1100}

  image = read_local_image(image_file_path)
  gray_image = convert_to_grayscale(image)
  _, binary_image = convert_to_binary_image(gray_image, binary_threshold)
  candidate_defects = find_candidate_defect_contours(
    binary_image, min_area, max_area, critical_roi
  )
  status, reasons = judge_ok_ng(candidate_defects, max_defect_count)
  result_image = draw_defect_annotation_image(
    candidate_defects, critical_roi, status, reasons, image
  )
  result_json = build_result_json(
    image_file_path,
    min_area,
    max_area,
    max_defect_count,
    binary_threshold,
    candidate_defects,
    status,
    reasons,
  )
  save_outputs(outputs_dir, result_image, binary_image, result_json)


if __name__ == "__main__":
  main()
