from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent


def yolo_detect_train():
  dataset_path = BASE_DIR / "dataset" / "dataset.yaml"
  project_path = BASE_DIR / "runs"
  project_path.mkdir(parents=True, exist_ok=True)
  model = YOLO("yolov8n.pt")

  results = model.train(
    data=str(dataset_path),
    epochs=1,
    imgsz=640,
    # batch=16,
    # device=0,
    # workers=4,
    batch=4,
    device="cpu",
    project=str(project_path),
    name="dpi_button_smoke_test",
  )
  return results


if __name__ == "__main__":
  results = yolo_detect_train()
  print(results)
