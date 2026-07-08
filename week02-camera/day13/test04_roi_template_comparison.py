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


def validate_box(box_config, image, name):
  x, y, w, h = box_config
  image_height, image_width = image.shape[:2]

  if x < 0 or y < 0:
    raise ValueError(f"{name} x/y must be >=0")
  if w <= 0 or h <= 0:
    raise ValueError(f"{name} w/h must be > 0")
  if x + w > image_width:
    raise ValueError(f"{name} exceeds image width")
  if y + h > image_height:
    raise ValueError(f"{name} exceeds image height")

  return True


def crop_box(box_config, image, name):
  x = box_config["x"]
  y = box_config["y"]
  w = box_config["w"]
  h = box_config["h"]
  validate_box((x, y, w, h), image, name)
  return image[y : y + h, x : x + w]


def preprocess_roi(config, roi_image):
  import cv2

  prep_cfg = config.get("preprocess", {})
  kernel_size = tuple(prep_cfg["gaussian_kernel_size"])
  enable = prep_cfg["binary"]["enable"]
  thresh_val = prep_cfg["binary"]["threshold"]
  max_val = prep_cfg["binary"]["max_value"]
  mode_str = prep_cfg["binary"]["type"]
  gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, kernel_size, 0)
  if enable:
    if mode_str == "BINARY":
      cv_mode = cv2.THRESH_BINARY
    elif mode_str == "BINARY_INV":
      cv_mode = cv2.THRESH_BINARY_INV
    elif mode_str == "OTSU":
      cv_mode = cv2.THRESH_BINARY | cv2.THRESH_OTSU
    elif mode_str == "OTSU_INV":
      cv_mode = cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    threshold, binary = cv2.threshold(blur, thresh_val, max_val, cv_mode)

  return gray, blur, binary, threshold


def find_best_contours(config, binary, image):
  """寻找最适合的轮廓

  Args:
      config(JSON):配置
      binary (ndarray): 二值图
      image (ndarray): 原图

  Returns:
      valid_contours:有效轮廓
  """
  import cv2

  # 找轮廓
  contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  # 有效轮廓数组
  valid_contours = []
  cnt_filter_cfg = config.get("contour_filter", {})
  # 循环筛选有效轮廓
  for contour in contours:
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / h
    # 按面积过滤
    if area <= cnt_filter_cfg["min_area"]:
      continue
    # 按宽高比过滤
    valid_contours.append(
      {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "area": area,
        "aspect_ratio": aspect_ratio,
        "contour": contour,
      }
    )

  valid_contours = sorted(valid_contours, key=lambda cnt: cnt["area"], reverse=True)
  return valid_contours[0] if len(valid_contours) != 0 else {}, contours


def local_box_global_box(config, local_box):
  local_x, local_y, local_w, local_h = local_box

  global_x = config["roi"]["x"] + local_x
  global_y = config["roi"]["y"] + local_y
  return global_x, global_y, local_w, local_h


def run_template_matching(config, roi_image, template):
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


def draw_bbox(config, image, contour_box, template_box):
  import cv2

  # 绘制框体颜色粗细配置
  draw_config = config.get("draw", "")
  contour_thickness = draw_config["contour"]["thickness"]
  contou_color = tuple(draw_config["contour"]["color"])
  roi_thickness = draw_config["roi"]["thickness"]
  roi_color = tuple(draw_config["roi"]["color"])
  template_thickness = draw_config["template"]["thickness"]
  template_color = draw_config["template"]["color"]

  # roi
  roi_config = config.get("roi", {})
  roi_x = roi_config["x"]
  roi_y = roi_config["y"]
  roi_w = roi_config["w"]
  roi_h = roi_config["h"]

  # template
  t_x, t_y, t_w, t_h = template_box
  # best_contour
  c_x, c_y, c_w, c_h = contour_box

  marked = image.copy()
  cv2.rectangle(
    marked,
    (roi_x, roi_y),
    (roi_x + roi_w, roi_y + roi_h),
    roi_color,
    roi_thickness,
    cv2.LINE_AA,
  )
  cv2.rectangle(
    marked,
    (t_x, t_y),
    (t_x + t_w, t_y + t_h),
    template_color,
    template_thickness,
    cv2.LINE_AA,
  )
  cv2.rectangle(
    marked,
    (c_x, c_y),
    (c_x + c_w, c_y + c_h),
    contou_color,
    contour_thickness,
    cv2.LINE_AA,
  )
  return marked


def build_comparison_json(
  config,
  path,
  contours,
  best_contour,
  best_val,
  contour_box,
  contour_local_box,
  template_box,
  template_local_box,
):
  roi_config = config.get("roi", {})
  match_config = config.get("template_matching", {})
  roi_x = roi_config["x"]
  roi_y = roi_config["y"]
  roi_w = roi_config["w"]
  roi_h = roi_config["h"]
  c_x, c_y, c_w, c_h = contour_box
  c_l_x, c_l_y, c_l_w, c_l_h = contour_local_box
  t_x, t_y, t_w, t_h = template_box
  t_l_x, t_l_y, t_l_w, t_l_h = template_local_box
  return {
    "image_name": path.name,
    "roi": {"x": roi_x, "y": roi_y, "w": roi_w, "h": roi_h},
    "contour_detection": {
      "raw_contour_count": len(contours),
      "valid": False if best_contour is None else True,
      "local_box": {
        "x": c_l_x,
        "y": c_l_y,
        "w": c_l_w,
        "h": c_l_h,
      },
      "global_box": {"x": c_x, "y": c_y, "w": c_w, "h": c_h},
      "area": best_contour["area"],
    },
    "template_matching": {
      "method": match_config["method"],
      "best_score": best_val,
      "best_loc_global": {"x": t_x, "y": t_y},
      "best_loc_roi": {"x": t_l_x, "y": t_l_y},
      "template_size": {"width": t_l_w, "height": t_l_h},
    },
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


def save_outputs(config, roi, binary, template, result, json_data):
  """保存结果

  Args:
      image (ndarray): 原图
      gray (ndarray): 灰度图
      blur (ndarray): 高斯滤波图
      binary (ndarray): 二值图
      result (ndarray): 标注结果图
      json_data (JSON): 结果JSON
  """
  import json

  outputs_config = config.get("outputs", {})
  OUTPUTS_DIR = BASE_DIR / "outputs" / outputs_config["dir_name"]
  OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
  roi_path = OUTPUTS_DIR / "roi.png"
  binary_path = OUTPUTS_DIR / "binary.png"
  template_path = OUTPUTS_DIR / "template.png"
  result_path = OUTPUTS_DIR / "result.png"
  json_path = OUTPUTS_DIR / "comparison.json"

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)
  if roi is not None:
    save_image(roi_path, roi)
  if binary is not None:
    save_image(binary_path, binary)
  if template is not None:
    save_image(template_path, template)
  if result is not None:
    save_image(result_path, result)


def print_image_contour_template_stats(
  path,
  contours,
  best_val,
  contour_box,
  contour_local_box,
  template_box,
  template_local_box,
):
  c_x, c_y, c_w, c_h = contour_box
  c_l_x, c_l_y, c_l_w, c_l_h = contour_local_box
  t_x, t_y, t_w, t_h = template_box
  t_l_x, t_l_y, t_l_w, t_l_h = template_local_box
  print(f"图片名称:{path.name}\n总轮廓数：{len(contours)}")
  print(
    f"best_contour global-> x:{c_x} y:{c_y} w:{c_w} h:{c_h} roi-> x:{c_l_x} y:{c_l_y} w:{c_l_w} h:{c_l_h}\n"
    f"template best_score->{best_val} best_loc_global-> x:{t_x} y:{t_y} w:{t_w} h:{t_h} best_loc_roi-> x:{t_l_x} y:{t_l_y} w:{t_l_w} h:{t_l_h}"
  )


def main():
  config = read_config_json()
  images = read_local_images(config)
  roi_config = config.get("roi", {})
  template_config = config.get("template_matching", {}).get("template", {})

  for image, path in images:
    roi_image = crop_box(roi_config, image, "ROI")
    gray, blur, binary, threshold = preprocess_roi(config, roi_image)
    best_contour, contours = find_best_contours(config, binary, roi_image)
    contour_local_box = (
      best_contour["x"],
      best_contour["y"],
      best_contour["w"],
      best_contour["h"],
    )
    contour_box = local_box_global_box(config, contour_local_box)

    template_image = crop_box(template_config, image, "Template")
    template_h, template_w = template_image.shape[:2]
    best_val, best_loc, min_val, min_loc = run_template_matching(
      config, roi_image, template_image
    )
    template_local_box = (best_loc[0], best_loc[1], template_w, template_h)
    template_box = local_box_global_box(config, template_local_box)

    result = draw_bbox(config, image, contour_box, template_box)
    json_data = build_comparison_json(
      config,
      path,
      contours,
      best_contour,
      best_val,
      contour_box,
      contour_local_box,
      template_box,
      template_local_box,
    )

    save_outputs(config, roi_image, binary, template_image, result, json_data)
    print_image_contour_template_stats(
      path,
      contours,
      best_val,
      contour_box,
      contour_local_box,
      template_box,
      template_local_box,
    )


if __name__ == "__main__":
  main()
