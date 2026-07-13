from pathlib import Path


MODEL_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo\day16\runs\dpi_button_smoke_test-2\weights\best.pt"
)
IMAGE_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo\day16\dataset\images\val\dpi_button_0005.png"
)
OUTPUT_DIR = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo\day17\outputs\opencv_report"
)


def predict_image(model_path, image_path, conf):
  """
  根据图片获取YOLO识别结果
  """
  import cv2
  from ultralytics import YOLO

  image = cv2.imread(str(image_path))
  if image is None:
    raise RuntimeError(f"图片读取失败：{image_path}")
  if not model_path.exists():
    raise RuntimeError(f"YOLO模型加载失败：{model_path}")

  model = YOLO(str(model_path))
  results = model.predict(source=image, save=False, verbose=False, conf=conf)
  return image, results


def extract_detections(result):
  """
  解析YOLO推理结果，将数据结构转换为字典结构
  """
  class_dict = result.names
  detections = []
  for index, box in enumerate(result.boxes):
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int).tolist()
    w = x2 - x1
    h = y2 - y1
    conf = box.conf.item()
    cls_id = int(box.cls.item())
    class_name = class_dict[cls_id]
    detections.append(
      {
        "index": index + 1,
        "class_id": cls_id,
        "class_name": class_name,
        "confidence": conf,
        "bbox_xyxy": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "bbox_size": {"width": w, "height": h},
      }
    )

  return detections


def draw_report(image, detections, status, reason):
  """
  根据YOLO推理结果，在图片进行标注
  """
  import cv2

  if status == "OK":
    font_color = (0, 255, 0)
  else:
    font_color = (0, 0, 255)
  result_image = image.copy()
  image_height, image_width = image.shape[:2]
  cv2.rectangle(result_image, (0, 0), (image_width, 60), (64, 64, 64), -1)
  font = cv2.FONT_HERSHEY_SIMPLEX
  cv2.putText(
    result_image,
    f"Status:{status}  Reason:{reason}",
    (20, 40),
    font,
    0.8,
    font_color,
    1,
    cv2.LINE_AA,
  )
  for detect in detections:
    bbox_xyxy = detect["bbox_xyxy"]
    bbox_x1y1 = (bbox_xyxy["x1"], bbox_xyxy["y1"])
    bbox_x2y2 = (bbox_xyxy["x2"], bbox_xyxy["y2"])
    bbox_text_xy = (bbox_xyxy["x1"], max(bbox_xyxy["y1"] + 20, 30))
    cv2.rectangle(result_image, bbox_x1y1, bbox_x2y2, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(
      result_image,
      f"class_name:{detect['class_name']} confidence:{detect['confidence']:.3f}",
      bbox_text_xy,
      font,
      0.8,
      (0, 255, 255),
      1,
      cv2.LINE_AA,
    )

  return result_image


def build_report_json(image_path, model_path, status, reason, detections):
  """
  构建report的JSON数据
  """
  json_data = {
    "input_image": str(image_path),
    "model_path": str(model_path),
    "box_count": len(detections),
    "status": status,
    "reason": reason,
    "detections": detections,
  }
  return json_data


def save_outputs(result_path, json_path, result_image, data):
  """
  保存图片和JSON
  """
  import cv2
  import json

  saved_result = cv2.imwrite(str(result_path), result_image)
  if not saved_result:
    raise RuntimeError(f"保存图片失败：{result_path}")
  if data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)


def judge_ok_ng(min_confidence, expected_class_name, expected_count, detections):
  """
  使用解析后的检测数据判断OK/NG
  """
  has_class_detection_box = any(
    item.get("class_name") == expected_class_name for item in detections
  )
  matched_confs = [
    item["confidence"]
    for item in detections
    if item.get("class_name") == expected_class_name
  ]
  matched_count = len([conf for conf in matched_confs if conf >= min_confidence])
  has_low_conf = any(conf < min_confidence for conf in matched_confs)
  status, reason = "OK", "all_match_ok"
  if len(detections) == 0:
    status, reason = "NG", "no_detection"
  elif not has_class_detection_box:
    status, reason = "NG", "expected_class_not_found"
  elif has_low_conf:
    status, reason = "NG", "low_confidence"
  elif matched_count != expected_count:
    status, reason = "NG", "count_mismatch"
  return status, reason


def main():
  conf = 0.1
  expected_class_name = "dpi_button"
  expected_count = 1
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  json_path = OUTPUT_DIR / "report.json"
  result_path = OUTPUT_DIR / "result.png"

  image, results = predict_image(MODEL_PATH, IMAGE_PATH, conf)
  detections = extract_detections(results[0])
  status, reason = judge_ok_ng(conf, expected_class_name, expected_count, detections)
  result_image = draw_report(image, detections, status, reason)
  json_data = build_report_json(IMAGE_PATH, MODEL_PATH, status, reason, detections)
  save_outputs(result_path, json_path, result_image, json_data)


if __name__ == "__main__":
  main()
