from pathlib import Path
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent


def read_config_json():
  """加载JSON配置文件"""
  import json

  config_path = BASE_DIR / "config.json"
  with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
  return config


def read_local_images(config):
  """
  读取本地图片
  """
  import cv2

  images = []
  local_img_cfg = config.get("source", {}).get("local", {})
  dir_path = BASE_DIR / local_img_cfg["dir_path"]
  read_count = local_img_cfg["read_count"]
  valid_extensions = local_img_cfg["valid_extensions"]
  if not dir_path.exists():
    return images
  for index, file_path in enumerate(dir_path.iterdir()):
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append(
          {"image": image, "source_id": file_path.name, "source_type": "local"}
        )
    if len(images) == read_count:
      break
  return images


def extract_detections(result):
  """
  解析YOLO推理结果，将数据结构转化为结构化的字典列表
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


def build_json_payload(
  config, image_name, model_name, detections, status, reason, matched_count
):
  """
  将解析后的检测数据与图像数据拼接，生成JSON结构
  """
  yolo_cfg = config.get("yolo", {})
  min_confidence = yolo_cfg["min_confidence"]
  expected_class_name = yolo_cfg["expected_class_name"]
  expected_count = yolo_cfg["expected_count"]

  json_data = {
    "image_path": image_name,
    "model": model_name,
    "box_count": len(detections),
    "judge": {
      "expected_class_name": expected_class_name,
      "min_confidence": min_confidence,
      "expected_count": expected_count,
      "matched_count": matched_count,
      "status": status,
      "reason": reason,
    },
    "detections": detections,
  }
  return json_data


def judge_ok_ng(config, detections):
  """
  使用解析后的检测数据判断OK/NG
  """
  yolo_cfg = config.get("yolo", {})
  min_confidence = yolo_cfg["min_confidence"]
  expected_class_name = yolo_cfg["expected_class_name"]
  expected_count = yolo_cfg["expected_count"]
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
  return status, reason, matched_count


def save_json(config, json_data):
  import json

  outputs_cfg = config.get("outputs", {})
  outputs_path = BASE_DIR / outputs_cfg["base_dir"]
  outputs_path.mkdir(parents=True, exist_ok=True)
  json_path = outputs_path / outputs_cfg["data"]["result_filename"]

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)


def val_yolo_results(config):
  model_name = config.get("yolo", {}).get("model")
  images = read_local_images(config)
  if not images:
    raise RuntimeError("图片列表为空")
  model = YOLO(model_name)
  results = model.predict(source=images[0]["image"], save=True)
  detections = extract_detections(results[0])
  status, reason, matched_count = judge_ok_ng(config, detections)
  json_data = build_json_payload(
    config,
    images[0]["source_id"],
    model_name,
    detections,
    status,
    reason,
    matched_count,
  )
  save_json(config, json_data)


def main():
  config = read_config_json()
  sys_cfg = config.get("system", {})

  if sys_cfg["mode"] == "yolo":
    val_yolo_results(config)
  else:
    raise ValueError(f"运行模式：{sys_cfg['mode']}")


if __name__ == "__main__":
  main()
