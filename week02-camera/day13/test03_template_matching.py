import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def read_config_json():
  """读取配置JSON文件

  Returns:
      config: 配置
  """
  import json

  config_path = BASE_DIR / "config.json"
  with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
  return config


def read_local_images(config):
  """读取本地图片

  Args:
      config (JSON): 配置文件

  Returns:
      images: 图片数组
  """
  import cv2

  images = []
  local_images_config = config.get("local_images", {})
  dir_path = BASE_DIR / local_images_config["dir_path"]
  read_count = local_images_config["read_count"]
  valid_extensions = local_images_config["valid_extensions"]
  if not dir_path.exists():
    return images
  for index, file_path in enumerate(dir_path.iterdir()):
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append((image, file_path))
    if index + 1 == read_count:
      break
  return images


def validate_roi(roi_config, image):
  x, y, w, h = roi_config
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


def crop_roi(config, image):
  roi_config = config.get("roi", {})
  x = roi_config["x"]
  y = roi_config["y"]
  w = roi_config["w"]
  h = roi_config["h"]
  validate_roi((x, y, w, h), image)
  return image[y : y + h, x : x + w]


def template_matching(config, roi_image, template):
  import cv2

  method_map = {
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
  }
  template_config = config.get("template_matching", {})
  template_match_enable = template_config["enable"]
  method_str = template_config["method"]
  if template_match_enable:
    cv_method = method_map.get(method_str, cv2.TM_CCOEFF_NORMED)

    result = cv2.matchTemplate(roi_image, template, cv_method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    is_sqdiff = cv_method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]

    if is_sqdiff:
      best_val = min_val
      best_loc = min_loc
    else:
      best_val = max_val
      best_loc = max_loc
    return best_val, best_loc, min_val, min_loc
  raise RuntimeError("模板匹配功能未开启！")


def draw_best_match_box(config, best_loc, template, image):
  import cv2

  draw_config = config.get("draw", {})
  color = draw_config["template"]["color"]
  thickness = draw_config["template"]["thickness"]
  roi_config = config.get("roi", {})
  roi_x = roi_config["x"]
  roi_y = roi_config["y"]
  h, w = template.shape[:2]

  top_left_x = roi_x + best_loc[0]
  top_left_y = roi_y + best_loc[1]
  bottom_right_x = top_left_x + w
  bottom_right_y = top_left_y + h

  marked = image.copy()
  cv2.rectangle(
    marked,
    (top_left_x, top_left_y),
    (bottom_right_x, bottom_right_y),
    color,
    thickness,
    cv2.LINE_AA,
  )

  return marked


def validate_template(template_config, image):
  x, y, w, h = template_config
  image_height, image_width = image.shape[:2]

  if x < 0 or y < 0:
    raise ValueError("Template x/y must be >=0")
  if w <= 0 or h <= 0:
    raise ValueError("Template w/h must be > 0")
  if x + w > image_width:
    raise ValueError("Template exceeds image width")
  if y + h > image_height:
    raise ValueError("Template exceeds image height")

  return True


def crop_template_image(config, image):
  template_config = config.get("template_matching", {}).get("template", {})
  x = template_config["x"]
  y = template_config["y"]
  w = template_config["w"]
  h = template_config["h"]
  validate_template((x, y, w, h), image)
  template = image[y : y + h, x : x + w]
  return template


def match_result_to_json(config, best_val, best_loc, min_val, min_loc, template):
  match_config = config.get("template_matching", {})
  method_str = match_config["method"]
  roi_config = config.get("roi")
  roi_x = roi_config["x"]
  roi_y = roi_config["y"]
  height, width = template.shape[:2]
  return {
    "method": method_str,
    "best_score": float(best_val),
    "best_loc_roi": {
      "x": int(best_loc[0]),
      "y": int(best_loc[1]),
    },
    "best_loc_global": {
      "x": int(roi_x + best_loc[0]),
      "y": int(roi_y + best_loc[1]),
    },
    "min_score": float(min_val),
    "min_loc": {
      "x": int(min_loc[0]),
      "y": int(min_loc[1]),
    },
    "template": {"width": width, "height": height},
  }


def save_image(path, image):
  """保存图片

  Args:
      path (Path): 保存图片路径
      image (ndarray): 保存图片

  Raises:
      RuntimeError: 保存失败
  """
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_outputs(config, template, result, json_data):
  """保存结果

  Args:
      image (ndarray): 原图
      gray (ndarray): 灰度图
      blur (ndarray): 高斯滤波图
      binary (ndarray): 二值图
      result (ndarray): 标注结果图
      json_data (JSON): 结果JSON
  """
  outputs_config = config.get("outputs", {})
  OUTPUTS_DIR = BASE_DIR / "outputs" / outputs_config["dir_name"]
  OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
  template_path = OUTPUTS_DIR / "template.png"
  result_path = OUTPUTS_DIR / "result.png"
  json_path = OUTPUTS_DIR / "matching_result.json"

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)
  if template is not None:
    save_image(template_path, template)
  if result is not None:
    save_image(result_path, result)


def print_best_match_info(best_val, best_loc, template):
  h, w = template.shape[:2]
  print(f"best_val:{best_val} best_loc:{best_loc} template_size:{w} x {h}")


def main():
  config = read_config_json()
  images = read_local_images(config)

  for image, path in images:
    template = crop_template_image(config, image)
    roi_image = crop_roi(config, image)
    best_val, best_loc, min_val, min_loc = template_matching(
      config, roi_image, template
    )
    result = draw_best_match_box(config, best_loc, template, image)
    json_data = match_result_to_json(
      config, best_val, best_loc, min_val, min_loc, template
    )
    save_outputs(config, template, result, json_data)
    print_best_match_info(best_val, best_loc, template)


if __name__ == "__main__":
  main()
