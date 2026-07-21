from contextlib import contextmanager
from pathlib import Path

from config import cfg

BASE_DIR = Path(__file__).resolve().parent


def read_local_images():
  """
  读取本地图片
  """
  import cv2

  images = []
  local_image_dir = BASE_DIR / cfg.source.local.dir_path
  valid_extensions = cfg.source.local.valid_extensions
  read_count = cfg.source.local.read_count

  if not local_image_dir.exists():
    raise RuntimeError(f"图片输入目录不存在:{local_image_dir}")

  local_image_paths = sorted(local_image_dir.iterdir())
  for index, file_path in enumerate(local_image_paths):
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append({"image": image, "source_id": file_path, "source_type": "local"})
      if len(images) >= read_count:
        break
  return images


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


def crop_roi(image):
  """
  裁剪roi区域
  """
  roi_x = cfg.roi.x
  roi_y = cfg.roi.y
  roi_w = cfg.roi.w
  roi_h = cfg.roi.h
  roi_bbox = (roi_x, roi_y, roi_w, roi_h)
  validate_roi_coords(image, roi_bbox)
  return image[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]


@contextmanager
def ocr_session():
  """
  管理PaddleOCR生命周期
  """
  from paddleocr import PaddleOCR

  # 创建ocr实例
  ocr = PaddleOCR(
    use_textline_orientation=cfg.ocr.use_textline_orientation,
    enable_mkldnn=cfg.ocr.enable_mkldnn,
    lang=cfg.ocr.lang,
  )

  try:
    # 将ocr实例抛出给with使用
    yield ocr
  finally:
    # 离开with执行
    # 删除del进行垃圾回收
    del ocr


def extract_ocr_fields(image, ocr_model):
  """
  处理OCR图像结果并进行排序
  """
  import cv2

  if len(image.shape) == 2:
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  result = ocr_model.predict(image)
  if not result or not result[0]:
    return []

  texts = result[0].get("rec_texts", [])
  scores = result[0].get("rec_scores", [])
  boxes = result[0].get("dt_polys", [])

  combined = list(zip(boxes, texts, scores))
  if not combined:
    return []

  # 确定图像是否颠倒
  is_y_inverted = False
  doc_angle = result[0].get("doc_preprocessor_res", {}).get("angle")
  line_angles = result[0].get("textline_orientation_angles", [])

  if str(doc_angle) == "180" or doc_angle == 180:
    is_y_inverted = True
  elif line_angles:
    inverted_count = sum(1 for a in line_angles if str(a) == "180" or a == 180)
    if inverted_count > len(line_angles) / 2:
      is_y_inverted = True

  sorted_combined = sorted(
    combined,
    key=lambda item: min((point[1] for point in item[0]), default=0),
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


def build_ocr_result_json(detections, image_path):
  """
  构建ocr识别结果JSON
  """
  return {
    "input_image": str(image_path),
    "roi_bbox": {
      "x": cfg.roi.x,
      "y": cfg.roi.y,
      "width": cfg.roi.w,
      "height": cfg.roi.h,
    },
    "ocr_params": {
      "lang": cfg.ocr.lang,
      "use_textline_orientation": cfg.ocr.use_textline_orientation,
      "enable_mkldnn": cfg.ocr.enable_mkldnn,
    },
    "text_count": len(detections),
    "detections": detections,
  }


def save_image(path: Path, data):
  """
  保存单张图片
  """
  import cv2

  saved = cv2.imwrite(str(path), data)
  if not saved:
    raise RuntimeError(f"图片保存失败：{str(path)}")


def save_json(path: Path, data: dict):
  """
  JSON 数据保存
  """
  import json

  try:
    with open(path, "w", encoding="utf-8") as f:
      # ensure_ascii=False 保证中文正常显示，indent=2 保证格式美观
      json.dump(data, f, ensure_ascii=False, indent=2)
  except Exception as e:
    raise RuntimeError(f"JSON 保存失败: {path}, 错误: {e}")


def save_outputs(
  image_path,
  original_image=None,
  roi_image=None,
  result_image=None,
  result_data=None,
):
  image_name = Path(image_path).stem
  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  outputs_dir.mkdir(parents=True, exist_ok=True)

  # 保存任务
  save_tasks = [
    (
      cfg.outputs.images.save_original,
      f"{image_name}_original.png",
      original_image,
      save_image,
    ),
    (
      cfg.outputs.images.save_roi,
      f"{image_name}_roi.png",
      roi_image,
      save_image,
    ),
    (
      cfg.outputs.images.save_result,
      f"{image_name}_result.png",
      result_image,
      save_image,
    ),
    (
      cfg.outputs.data.save_result,
      f"{image_name}_result.json",
      result_data,
      save_json,
    ),
  ]

  # 执行保存
  for is_enable, file_name, data, save_method in save_tasks:
    if is_enable and data is not None:
      save_path = outputs_dir / file_name
      save_method(save_path, data)
    elif is_enable and data is None:
      print(f"配置文件开启了{file_name}的保存，但是没有传入对应数据，跳过")


def main():
  images = read_local_images()

  with ocr_session() as ocr:
    for item in images:
      roi_image = crop_roi(item["image"])
      result = extract_ocr_fields(roi_image, ocr)
      detections = build_detections(result)
      result_json = build_ocr_result_json(detections, item["source_id"])
      save_outputs(item["source_id"], roi_image=roi_image, result_data=result_json)


if __name__ == "__main__":
  main()
