import csv
from pathlib import Path

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent


def read_csv_file(path):
  """
  读取表格文件
  """
  header = []
  rows = []
  with open(path, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for index, row in enumerate(reader):
      if index == 0:
        header = row
      else:
        rows.append(row)
  return header, rows


def print_epoch_metrics(header, row):
  """
  打印box_loss、cls_loss、dfl_loss、mAP50
  """
  train_box_loss_index = header.index("train/box_loss")
  train_cls_loss_index = header.index("train/cls_loss")
  train_dfl_loss_index = header.index("train/dfl_loss")
  val_box_loss_index = header.index("val/box_loss")
  val_cls_loss_index = header.index("val/cls_loss")
  val_dfl_loss_index = header.index("val/dfl_loss")
  mAP50_index = header.index("metrics/mAP50(B)")
  if row:
    print(
      f"train/box_loss:{row[train_box_loss_index]} train/cls_loss:{row[train_cls_loss_index]} train/dfl_loss:{row[train_dfl_loss_index]} val/box_loss:{row[val_box_loss_index]} val/cls_loss:{row[val_cls_loss_index]} val/dfl_loss:{row[val_dfl_loss_index]} mAP50:{row[mAP50_index]}"
    )


def check_pt_exists(path):
  """
  检查pt文件是否存在
  """
  if Path(str(path)).exists():
    return True
  return False


def main():
  runs_path = BASE_DIR / "runs" / "dpi_button_smoke_test"
  results_path = runs_path / "results.csv"
  best_path = runs_path / "weights" / "best.pt"
  last_path = runs_path / "weights" / "last.pt"

  header, rows = read_csv_file(results_path)
  print(f"有{len(rows)}个epoch")
  print("最后一轮：")
  print_epoch_metrics(header, rows[-1])
  has_best_existes = check_pt_exists(best_path)
  has_last_existes = check_pt_exists(last_path)
  print(f"存在best.pt文件：{has_best_existes} 存在last.pt文件：{has_last_existes}")
  if has_best_existes:
    model = YOLO(str(best_path))
    print(f"best.pt的names为：{model.names}")


if __name__ == "__main__":
  main()
