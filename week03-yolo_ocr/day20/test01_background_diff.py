from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def read_local_image(path):
  """
  读取本地图片路径
  """
  import cv2

  validation_suffixes = [".jpg", ".png"]
  if not path.exists():
    raise RuntimeError(f"文件路径不存在:{path}")
  if path.suffix.lower() not in validation_suffixes:
    raise RuntimeError("当前读取的文件不是指定图片文件")

  image = cv2.imread(str(path))
  if image is None:
    raise RuntimeError("图片读取失败")
  return image


def convert_to_grayscale(image):
  """
  转化灰度图
  """
  import cv2

  if len(image.shape) == 3:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  return image


def filter_contours_by_min_area(min_area, image):
  """根据最小面积过滤噪声并返回有效轮廓"""
  import cv2

  valid_contours = []
  contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  for contour in contours:
    area = cv2.contourArea(contour)
    if area >= min_area:
      valid_contours.append(contour)
  return valid_contours


def draw_defect_boxes(contours, image):
  """
  绘制缺陷区域框
  """
  import cv2

  if len(image.shape) == 2:
    marked = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  else:
    marked = image.copy()
  defects = []
  for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(marked, (x, y), (x + w, y + h), (0, 0, 255), 1, cv2.LINE_AA)
    defects.append({"x": x, "y": y, "w": w, "h": h})
  return marked, defects


def judge_ok_ng(contours):
  """
  简单判断OK还是NG
  """
  if len(contours) > 0:
    return "NG"
  return "OK"


def build_result_json(
  normal_image_path, defect_image_path, threshold, min_area, status, defects
):
  """
  构建结果JSON
  """
  return {
    "normal_image": str(normal_image_path),
    "defect_image": str(defect_image_path),
    "diff_threshold": threshold,
    "min_area": min_area,
    "diff_count": len(defects),
    "result": status,
    "defects": defects,
  }


def save_image(path, image):
  import cv2

  if image is not None:
    saved = cv2.imwrite(str(path), image)
    if not saved:
      raise RuntimeError(f"图片保存失败：{path}")


def save_outputs(outputs_dir, result_image, binary_image, diff_image, result_json):
  """
  保存结果图，结果JSON
  """
  import json

  outputs_dir.mkdir(parents=True, exist_ok=True)
  result_image_path = outputs_dir / "result.png"
  result_json_path = outputs_dir / "result.json"
  binary_image_path = outputs_dir / "binary.png"
  diff_image_path = outputs_dir / "diff.png"

  save_image(result_image_path, result_image)
  save_image(binary_image_path, binary_image)
  save_image(diff_image_path, diff_image)
  with open(result_json_path, "w", encoding="utf-8") as f:
    json.dump(result_json, f, indent=2, ensure_ascii=False)


def subtract_background(normal, defect):
  """
  背景差分
  """
  import cv2

  if normal is None or defect is None:
    raise ValueError("标准图或待测图为空！")

  if normal.shape != defect.shape:
    raise RuntimeError("标准图与待测图尺寸或通道数不匹配")

  return cv2.absdiff(normal, defect)


def main():
  import cv2

  threshold = 30
  min_area = 300
  inputs_dir = BASE_DIR / "inputs"
  outputs_dir = BASE_DIR / "outputs" / "background_diff"
  normal_image_path = inputs_dir / "normal.png"
  defect_image_path = inputs_dir / "defect.png"

  normal_image = read_local_image(normal_image_path)
  defect_image = read_local_image(defect_image_path)
  normal_gray = convert_to_grayscale(normal_image)
  defect_gray = convert_to_grayscale(defect_image)
  diff = subtract_background(normal_gray, defect_gray)
  _, binary = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
  valid_contours = filter_contours_by_min_area(min_area, binary)
  marked, defects = draw_defect_boxes(valid_contours, defect_image)
  status = judge_ok_ng(valid_contours)
  result_json = build_result_json(
    normal_image_path, defect_image_path, threshold, min_area, status, defects
  )
  save_outputs(
    outputs_dir,
    result_image=marked,
    result_json=result_json,
    diff_image=diff,
    binary_image=binary,
  )


if __name__ == "__main__":
  main()
