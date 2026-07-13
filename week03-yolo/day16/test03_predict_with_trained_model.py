from pathlib import Path

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "runs" / "dpi_button_smoke_test-2" / "weights" / "best.pt"
IMAGE_PATH = BASE_DIR / "dataset" / "images" / "val" / "dpi_button_0005.png"
OUTPUT_DIR = BASE_DIR / "outputs" / "trained_model_predict"


def yolo_detect_results(model_path, image):
  """
  使用best.pt模型获取检测框结果
  """
  model = YOLO(str(model_path))

  results = model.predict(
    source=image,
    conf=0.1,
    save=False,
    verbose=False,
  )
  return results


def read_local_image(image_path):
  """
  根据路径读取本地图片
  """
  import cv2

  image = cv2.imread(str(image_path))
  if image is None:
    raise RuntimeError(f"图片读取失败：{image_path}")
  return image


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


def save_image(path, image):
  """
  保存图片
  """
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def main():
  image = read_local_image(IMAGE_PATH)
  results = yolo_detect_results(MODEL_PATH, image)
  detections = extract_detections(results[0])
  print(f"box_count: {len(detections)}")
  for detect in detections:
    print(detect)

  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  result_path = OUTPUT_DIR / "result.png"
  annotated = results[0].plot()
  save_image(result_path, annotated)


if __name__ == "__main__":
  main()
