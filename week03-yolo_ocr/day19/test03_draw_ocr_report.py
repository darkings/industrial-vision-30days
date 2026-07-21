from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from config import cfg


BASE_DIR = Path(__file__).resolve().parent


def load_json_results(file_type="result"):
  """
  读取JSON文件
  """
  import json

  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  data_cfg = cfg.outputs.data

  if not outputs_dir.exists():
    return []

  # 读取汇总文件
  if file_type == "summary":
    summary_path = outputs_dir / data_cfg.summary_filename
    if not summary_path.exists():
      raise RuntimeError(f"未找到汇总文件：{summary_path}")

    try:
      with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      raise RuntimeError(f"读取汇总文件失败:{e}")

  if file_type != "result" and file_type != "rule":
    raise RuntimeError(f"不支持的文件类型:{file_type}")

  # 匹配文件：根据后缀名匹配文件
  result_jsons = []
  for file_path in outputs_dir.glob("*.json"):
    # 判断当前文件类型
    is_rule_type = file_path.name.endswith(f"_{data_cfg.rule_result_filename}")
    is_result_type = file_path.name.endswith(f"_{data_cfg.result_filename}")

    # 排除过滤
    if file_type == "result":
      if not (is_result_type and not is_rule_type):
        continue
    if file_type == "rule":
      if not is_rule_type:
        continue

    # 读取JOSN文件
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        result_jsons.append(data)
    except json.JSONDecodeError:
      print(f"JSON文件不是合法的JSON格式 路径：{file_path}")
    except Exception as e:
      print(f"JSON文件读取失败：{e} 路径：{file_path}")
  return result_jsons


def read_image(image_path):
  """
  根据路径读取图片
  """
  import cv2

  image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
  if image is None:
    raise ValueError(f"Failed to read image: {image_path}")

  return image


def draw_bbox(type="roi", image=None, bbox_polygon=[]):
  """
  绘制框体
  """
  import cv2

  if len(image.shape) == 3:
    result_image = image.copy()
  else:
    result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  if type == "roi":
    color = cfg.draw.roi.color
    thickness = cfg.draw.roi.thickness
    x1, y1 = cfg.roi.x, cfg.roi.y
    x2, y2 = cfg.roi.x + cfg.roi.w, cfg.roi.y + cfg.roi.h
  elif type == "background":
    color = (64, 64, 64)
    thickness = -1
    _, image_width = image.shape[:2]
    x1, y1 = 0, 0
    x2, y2 = image_width, 60
  elif type == "ocr":
    if len(bbox_polygon) != 4:
      raise RuntimeError("bbox_polygon的长度必须为4")
    color = cfg.draw.ocr.color
    thickness = cfg.draw.ocr.thickness
    roi_x = cfg.roi.x
    roi_y = cfg.roi.y

    # 提取所有x和y
    x_coords = [point[0] for point in bbox_polygon]
    y_coords = [point[1] for point in bbox_polygon]

    x1, y1 = int(min(x_coords)) + roi_x, int(min(y_coords)) + roi_y
    x2, y2 = int(max(x_coords)) + roi_x, int(max(y_coords)) + roi_y

  cv2.rectangle(result_image, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
  return result_image


def draw_text(
  type="result", image=None, status=None, reasons=[], bbox_polygon=[], text=""
):
  """
  绘制文字
  """
  import cv2

  if len(image.shape) == 3:
    result_image = image.copy()
  else:
    result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  if type == "result":
    if status is None:
      raise RuntimeError("当类型为result时，参数必须传递status")
    if status:
      color = (0, 255, 0)
    else:
      color = (0, 0, 255)
    x, y = 10, 10
    reason_texts = [text for text in reasons]
    label_text = f"Status:{'OK' if status else 'NG'} {f'Reason:{",".join(reason_texts)}' if len(reasons) != 0 else ''}"
    font_size = 22
  elif type == "text":
    if len(bbox_polygon) != 4:
      raise RuntimeError("bbox_polygon的长度必须为4")
    x_coords = [point[0] for point in bbox_polygon]
    y_coords = [point[1] for point in bbox_polygon]
    roi_x = cfg.roi.x
    roi_y = cfg.roi.y

    x, y = int(min(x_coords)) + roi_x + 5, max(int(max(y_coords)) + roi_y - 30, 30)
    label_text = text
    font_size = 20
    color = (0, 255, 0)
  else:
    raise RuntimeError(f"不支持的类型:{type}")

  try:
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
  except IOError:
    font = ImageFont.load_default()

  pil_img = Image.fromarray(result_image)
  draw = ImageDraw.Draw(pil_img)
  draw.text((x, y), label_text, fill=color, font=font)
  result_image = np.array(pil_img)
  return result_image


def save_image(path: Path, data):
  """
  保存单张图片
  """
  import cv2

  saved = cv2.imwrite(str(path), data)
  if not saved:
    raise RuntimeError(f"图片保存失败：{str(path)}")


def main():
  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  raw_results = load_json_results(file_type="result")
  rule_results = load_json_results(file_type="rule")
  results = zip(raw_results, rule_results)
  for raw_data, rule_data in results:
    input_image_path = raw_data.get("input_image", "")
    result_path = outputs_dir / f"{Path(input_image_path).stem}_report.png"
    status = rule_data.get("status", "")
    reasons = rule_data.get("reasons", [])

    image = read_image(input_image_path)
    result_image = draw_bbox(type="background", image=image)
    result_image = draw_bbox(type="roi", image=result_image)
    result_image = draw_text(
      type="result", image=result_image, status=status, reasons=reasons
    )
    detections = raw_data.get("detections", [])
    for detect in detections:
      text = detect.get("text", "")
      bbox_polygon = detect.get("bbox_polygon", [])
      result_image = draw_bbox(
        type="ocr", image=result_image, bbox_polygon=bbox_polygon
      )
      result_image = draw_text(
        type="text", image=result_image, bbox_polygon=bbox_polygon, text=text
      )
    save_image(result_path, result_image)


if __name__ == "__main__":
  main()
