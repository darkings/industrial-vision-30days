from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
IMAGE_FILE_PATH = BASE_DIR / "inputs" / "image.png"
OUTPUTS_DIR = BASE_DIR / "outputs" / "extract_ocr_results"


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

  return gray_image, binary_image, threshold


def save_image(path, image):
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_outputs(out_dir, original_image, gray_image, binary_image):
  """
  多张图片保存
  """
  out_dir.mkdir(parents=True, exist_ok=True)
  original_path = out_dir / "roi_original.png"
  gray_path = out_dir / "roi_gray.png"
  binary_path = out_dir / "roi_binary.png"

  if original_image is not None:
    save_image(original_path, original_image)
  if gray_image is not None:
    save_image(gray_path, gray_image)
  if binary_image is not None:
    save_image(binary_path, binary_image)

  return original_path, gray_path, binary_path


def build_summary_json(
  image_path, out_dir, roi_bbox, roi_image, inverse, use_otsu, threshold, image_paths
):
  """
  构建 OCR ROI预处理摘要
  """
  roi_x, roi_y, roi_w, roi_h = roi_bbox
  roi_image_height, roi_image_width, roi_image_channels = roi_image.shape
  original_path, gray_path, binary_path = image_paths

  return {
    "input_image": str(image_path),
    "output_dir": str(out_dir),
    "roi_bbox": {"x": roi_x, "y": roi_y, "width": roi_w, "height": roi_h},
    "roi_shape": {
      "height": roi_image_height,
      "width": roi_image_width,
      "channels": roi_image_channels,
    },
    "preprocess": {
      "use_otsu": use_otsu,
      "inverse": inverse,
      "threshold": threshold,
    },
    "outputs": {
      "roi_original": str(original_path),
      "roi_gray": str(gray_path),
      "roi_binary": str(binary_path),
    },
  }


def save_json(out_dir, json_name, json_data):
  """
  保存json文件
  """
  import json

  out_dir.mkdir(parents=True, exist_ok=True)
  json_path = out_dir / f"{json_name}.json"

  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)


def extract_ocr_fields(image, use_textline_orientation, enable_mkldnn, lang):
  """
  通过OCR提取 rec_texts / rec_scores / dt_polys
  """
  from paddleocr import PaddleOCR

  ocr = PaddleOCR(
    use_textline_orientation=use_textline_orientation,
    enable_mkldnn=enable_mkldnn,
    lang=lang,
  )
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


def build_ocr_result_json(
  detections, image_path, roi_bbox, use_textline_orientation, enable_mkldnn, lang
):
  x, y, w, h = roi_bbox
  return {
    "input_image": str(image_path),
    "roi_bbox": {"x": x, "y": y, "width": w, "height": h},
    "ocr_params": {
      "lang": lang,
      "use_textline_orientation": use_textline_orientation,
      "enable_mkldnn": enable_mkldnn,
    },
    "text_count": len(detections),
    "detections": detections,
  }


def main():
  inverse = False
  use_otsu = True
  roi_bbox = (15, 20, 270, 180)
  use_textline_orientation = True
  enable_mkldnn = False
  lang = "ch"

  image = read_local_image(IMAGE_FILE_PATH)
  roi_image = crop_roi(image, roi_bbox)
  gray_image, binary_image, threshold = preprocess_image(
    roi_image, inverse=inverse, use_otsu=use_otsu
  )
  image_paths = save_outputs(OUTPUTS_DIR, roi_image, gray_image, binary_image)
  summary_json_data = build_summary_json(
    IMAGE_FILE_PATH,
    OUTPUTS_DIR,
    roi_bbox,
    roi_image,
    inverse,
    use_otsu,
    threshold,
    image_paths,
  )
  save_json(OUTPUTS_DIR, "summary", summary_json_data)

  combined = extract_ocr_fields(
    roi_image, use_textline_orientation, enable_mkldnn, lang
  )
  detections = build_detections(combined)
  ocr_result_json = build_ocr_result_json(
    detections, IMAGE_FILE_PATH, roi_bbox, use_textline_orientation, enable_mkldnn, lang
  )
  save_json(OUTPUTS_DIR, "ocr_result", ocr_result_json)


if __name__ == "__main__":
  main()
