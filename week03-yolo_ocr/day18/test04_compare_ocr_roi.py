from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "inputs" / "image.png"
OUTPUTS_DIR = BASE_DIR / "outputs" / "compare_ocr_roi"


def read_local_image(path):
  """
  根据路径读取本地图片
  """
  import cv2

  image = cv2.imread(str(path))
  if image is None:
    raise RuntimeError(f"图片读取失败：{path}")
  return image


def validate_roi_coords(image, roi_bbox):
  """
  验证 ROI 坐标是否在图像范围内
  """
  x, y, w, h = roi_bbox
  image_height, image_width = image.shape[:2]

  if x < 0 or y < 0:
    raise ValueError("ROI x/y must be >=0")
  if w <= 0 or h <= 0:
    raise ValueError("ROI w/h must be > 0")
  if x + w > image_width:
    raise ValueError("ROI exceeds image width")
  if y + h > image_height:
    raise ValueError("ROI exceeds image height")

  return True


def crop_roi(image, roi_bbox):
  """
  裁剪roi
  """
  x, y, w, h = roi_bbox
  validate_roi_coords(image, roi_bbox)
  return image[y : y + h, x : x + w]


def preprocess_image(
  image,
  inverse: bool = False,
  use_otsu: bool = True,
  thresh_val: int = 127,
  max_val: int = 255,
) -> tuple[np.ndarray, np.ndarray, float]:
  """
  图像预处理
  """
  import cv2

  # 根据传递过来的图像决定是否做灰度化
  if len(image.shape) == 2:
    gray_image = image.copy()
  else:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # 根据传递的inverse判断是正二值化还是反二值化
  binary_type = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY

  # 根据传递的use_otsu来动态组合
  if use_otsu:
    thresh_type = binary_type | cv2.THRESH_OTSU
  else:
    thresh_type = binary_type

  threshold, binary_image = cv2.threshold(
    gray_image,
    thresh_val,
    max_val,
    thresh_type,
  )

  return binary_image, threshold


def save_image(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_json(out_dir, json_name, json_data):
  """
  保存json文件
  """
  import json

  out_dir.mkdir(parents=True, exist_ok=True)
  json_path = out_dir / f"{json_name}.json"

  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)


def extract_ocr_fields(image):
  """
  通过OCR提取 rec_texts / rec_scores / dt_polys
  """
  import cv2
  from paddleocr import PaddleOCR

  ocr = PaddleOCR(
    use_textline_orientation=True,
    enable_mkldnn=False,
    lang="ch",
  )
  if len(image.shape) == 2:
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  results = ocr.predict(image)

  texts = results[0].get("rec_texts", [])
  scores = results[0].get("rec_scores", [])
  boxes = results[0].get("dt_polys", [])

  combined = zip(boxes, texts, scores)

  is_y_inverted = False
  doc_angle = results[0].get("doc_preprocessor_res", {}).get("angle")
  line_angles = results[0].get("textline_orientation_angles", [])
  if str(doc_angle) == "180" or doc_angle == 180:
    is_y_inverted = True
  elif line_angles:
    inverted_count = sum(1 for a in line_angles if str(a) == "180" or a == 180)
    if inverted_count > len(line_angles) / 2:
      is_y_inverted = True

  sorted_combined = sorted(
    combined,
    key=lambda item: min(point[1] for point in item[0]),
    reverse=is_y_inverted,
  )

  return sorted_combined


def build_detections(combined):
  """
  构建detections列表
  """
  detections = []
  for index, (box, text, confidence) in enumerate(combined):
    detections.append(
      {
        "index": index + 1,
        "text": str(text),
        "confidence": float(confidence),
        "bbox_polygon": box.tolist(),
      }
    )
  return detections


def build_compare_case_json(name, roi_bbox, roi_path, detections):
  x, y, w, h = roi_bbox
  return {
    "name": f"{name}_roi",
    "roi_bbox": {"x": x, "y": y, "width": w, "height": h},
    "roi_image": str(roi_path),
    "text_count": len(detections),
    "texts": detections,
  }


def build_compare_summary_json(input_path, cases):
  json_data = {
    "input_image": str(input_path),
    "cases": [],
  }
  for case in cases:
    json_data["cases"].append(case)
  return json_data


def main():
  tight_roi = (15, 20, 270, 180)
  loose_roi = (0, 0, 320, 207)
  OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
  tight_roi_path = OUTPUTS_DIR / "tight_roi.png"
  loose_roi_path = OUTPUTS_DIR / "loose_roi.png"

  image = read_local_image(IMAGE_FILE_PATH)
  tight_roi_image = crop_roi(image, tight_roi)
  tight_binary_image, _ = preprocess_image(tight_roi_image)
  loose_roi_image = crop_roi(image, loose_roi)
  loose_binary_image, _ = preprocess_image(loose_roi_image)

  tight_combined = extract_ocr_fields(tight_binary_image)
  loose_combined = extract_ocr_fields(loose_binary_image)

  tight_detections = build_detections(tight_combined)
  loose_detections = build_detections(loose_combined)

  save_image(tight_roi_path, tight_roi_image)
  save_image(loose_roi_path, loose_roi_image)

  tight_case_json = build_compare_case_json(
    "tight", tight_roi, tight_roi_path, tight_detections
  )
  loose_case_json = build_compare_case_json(
    "loose", loose_roi, loose_roi_path, loose_detections
  )
  cases = [tight_case_json, loose_case_json]
  compare_summary_json = build_compare_summary_json(IMAGE_FILE_PATH, cases)

  save_json(OUTPUTS_DIR, "compare_summary", compare_summary_json)


if __name__ == "__main__":
  main()
