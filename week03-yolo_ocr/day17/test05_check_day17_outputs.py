from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OUTPUTS_DIR = BASE_DIR / "outputs" / "batch_opencv_report"


def verify_output_completeness(outputs_dir, expected_count):
  """
  检查输出目录文件是否完整
  """
  report_png_dir = outputs_dir / "images"
  report_json_dir = outputs_dir / "json"
  summary_json_path = outputs_dir / "summary.json"
  summary_csv_path = outputs_dir / "summary.csv"
  failed_cases_json_path = outputs_dir / "failed_cases.json"
  failed_cases_csv_path = outputs_dir / "failed_cases.csv"

  report_png_count = len(list(report_png_dir.glob("*_report.png")))
  report_json_count = len(list(report_json_dir.glob("*_report.json")))

  has_all_pngs = report_png_count == expected_count
  has_all_jsons = report_json_count == expected_count
  output_dir_exists = outputs_dir.exists()
  summary_json_exists = summary_json_path.exists()
  summary_csv_exists = summary_csv_path.exists()
  failed_cases_csv_exists = failed_cases_csv_path.exists()
  failed_cases_json_exists = failed_cases_json_path.exists()
  all_ok = all(
    [
      has_all_pngs,
      has_all_jsons,
      output_dir_exists,
      summary_json_exists,
      summary_csv_exists,
      failed_cases_csv_exists,
      failed_cases_json_exists,
    ]
  )

  print(f"验证输出结构是否完整：{'OK' if all_ok else 'NG'}")
  print(f"batch_opencv_report目录：{output_dir_exists}")
  print(f"images目录是否有{expected_count}张report.png：{has_all_pngs}")
  print(f"json目录是否有{expected_count}个report.json：{has_all_jsons}")
  print(f"summary.json是否存在：{summary_json_exists}")
  print(f"summary.csv是否存在：{summary_csv_exists}")
  print(f"failed_cases.json是否存在：{failed_cases_json_exists}")
  print(f"failed_cases.csv是否存在：{failed_cases_csv_exists}")
  return all_ok


def main():
  expected_count = 5
  verify_output_completeness(OUTPUTS_DIR, expected_count)


if __name__ == "__main__":
  main()
