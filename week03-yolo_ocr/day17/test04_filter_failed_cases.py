from pathlib import Path

SUMMARY_JSON_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo_ocr\day17\outputs\batch_opencv_report\summary.json"
)
OUTPUT_JSON_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo_ocr\day17\outputs\batch_opencv_report\failed_cases.json"
)
OUTPUT_CSV_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo_ocr\day17\outputs\batch_opencv_report\failed_cases.csv"
)


def load_summary_json(json_path):
  """
  读取summary.json文件
  """
  import json

  with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

  return json_data


def filter_failed_summary(json_data):
  """
  summary json数据筛选失败结果
  """
  items = json_data["items"]
  detections = []
  for item in items:
    if item["status"] != "OK":
      detections.append(item)

  return detections


def write_failed_json(failed_json_path, detections):
  """
  写入json文件
  """
  import json

  json_data = {"failed_count": len(detections), "items": detections}
  if not failed_json_path.parent.exists():
    failed_json_path.parent.mkdir(parents=True, exist_ok=True)
  with open(failed_json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)


def write_failed_csv(failed_csv_path, detections):
  """
  写入csv文件
  """
  import csv

  fieldnames = [
    "image_name",
    "box_count",
    "status",
    "reason",
    "report_image",
    "report_json",
  ]
  if not failed_csv_path.parent.exists():
    failed_csv_path.parent.mkdir(parents=True, exist_ok=True)
  with open(failed_csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(detections)


def main():
  summary_json_data = load_summary_json(SUMMARY_JSON_PATH)
  detections = filter_failed_summary(summary_json_data)
  write_failed_csv(OUTPUT_CSV_PATH, detections)
  write_failed_json(OUTPUT_JSON_PATH, detections)


if __name__ == "__main__":
  main()



