from pathlib import Path

SUMMARY_JSON_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo\day17\outputs\batch_opencv_report\summary.json"
)
OUTPUT_CSV_PATH = Path(
  r"D:\Projects\industrial-vision-30days\week03-yolo\day17\outputs\batch_opencv_report\summary.csv"
)


def load_summary_json(json_path):
  """
  读取summary.json文件
  """
  import json

  with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

  return json_data


def write_summary_csv(items, csv_path):
  """
  写入summary.csv
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
  if not csv_path.parent.exists():
    csv_path.parent.mkdir(parents=True, exist_ok=True)
  with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(items)


def main():
  summary_json_data = load_summary_json(SUMMARY_JSON_PATH)
  items = summary_json_data["items"]
  write_summary_csv(items, OUTPUT_CSV_PATH)

  print(f"image_count: {summary_json_data['image_count']}")
  print(f"ok_count: {summary_json_data['ok_count']}")
  print(f"ng_count: {summary_json_data['ng_count']}")
  print(f"csv_path: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
  main()
