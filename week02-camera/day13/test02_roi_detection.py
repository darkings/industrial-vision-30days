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
  dir_path = BASE_DIR / config["local_images"]["dir_path"]
  read_count = config["local_images"]["read_count"]
  valid_extensions = config["local_images"]["valid_extensions"]
  if not dir_path.exists():
    return images
  for index, file_path in enumerate(dir_path.iterdir()):
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append({"tag": file_path, "image": image})
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
  x = config["roi"]["x"]
  y = config["roi"]["y"]
  w = config["roi"]["w"]
  h = config["roi"]["h"]
  validate_roi((x, y, w, h), image)
  return image[y : y + h, x : x + w]


def preprocess_roi(config, roi_image):
  import cv2

  kernel_size = tuple(config["preprocess"]["gaussian_kernel_size"])
  enable = config["preprocess"]["binary"]["enable"]
  thresh_val = config["preprocess"]["binary"]["threshold"]
  max_val = config["preprocess"]["binary"]["max_value"]
  mode_str = config["preprocess"]["binary"]["type"]
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


def find_valid_contours(config, binary, image):
  """寻找有效轮廓

  Args:
      binary (ndarray): 二值图
      image (ndarray): 原图

  Returns:
      valid_contours:有效轮廓
  """
  import cv2

  image_height, image_width = image.shape[:2]
  # 找轮廓
  contours, _ = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
  )
  # 有效轮廓数组
  valid_contours = []

  # 循环筛选有效轮廓
  for contour in contours:
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / h
    # 按面积过滤
    if area <= config["contour_filter"]["min_area"]:
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


def draw_roi_and_bbox(config, image, global_box):
  import cv2

  thickness = config["draw"]["rectangle"]["thickness"]
  color = tuple(config["draw"]["rectangle"]["color"])
  roi_x = config["roi"]["x"]
  roi_y = config["roi"]["y"]
  roi_w = config["roi"]["w"]
  roi_h = config["roi"]["h"]
  bbox_x, bbox_y, bbox_w, bbox_h = global_box

  marked = image.copy()
  cv2.rectangle(
    marked,
    (roi_x, roi_y),
    (roi_x + roi_w, roi_y + roi_h),
    color,
    thickness,
  )
  cv2.rectangle(
    marked,
    (bbox_x, bbox_y),
    (bbox_x + bbox_w, bbox_y + bbox_h),
    color,
    thickness,
  )
  return marked


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


def save_outputs(config, gray, binary, roi_image, result):
  OUTPUTS_DIR = BASE_DIR / "outputs" / config["outputs"]["dir_name"]
  OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
  gray_path = OUTPUTS_DIR / "gray.png"
  roi_path = OUTPUTS_DIR / "roi.png"
  binary_path = OUTPUTS_DIR / "binary.png"
  result_path = OUTPUTS_DIR / "result.png"

  if gray is not None:
    save_image(gray_path, gray)
  if binary is not None:
    save_image(binary_path, binary)
  if roi_image is not None:
    save_image(roi_path, roi_image)
  if result is not None:
    save_image(result_path, result)


def print_otsu_threshold_contour_boxes(threshold, contours, local_box, global_box):
  local_x, local_y, local_w, local_h = local_box
  global_x, global_y, global_w, global_h = global_box
  print(
    f"OTSU阈值：{threshold} | 轮廓数量：{len(contours)}\n"
    f"局部框信息-> x:{local_x} y:{local_y} w:{local_w} h:{local_h} \n"
    f"全图框信息-> x:{global_x} y:{global_y} w:{global_w} h:{global_h}"
  )


def main():
  config = read_config_json()
  images = read_local_images(config)

  for item in images:
    roi_image = crop_roi(config, item["image"])
    gray, _, binary, threshold = preprocess_roi(config, roi_image)

    contour, contours = find_valid_contours(config, binary, item["image"])
    if not contour:
      print("当前图未找到有效轮廓！")
      continue
    local_box = (contour["x"], contour["y"], contour["w"], contour["h"])
    global_box = local_box_global_box(config, local_box)
    result = draw_roi_and_bbox(config, item["image"], global_box)
    save_outputs(config, gray, binary, roi_image, result)
    print_otsu_threshold_contour_boxes(threshold, contours, local_box, global_box)


if __name__ == "__main__":
  main()
