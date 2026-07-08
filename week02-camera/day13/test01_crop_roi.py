import json
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"


def read_config_json():
  with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    return json.load(f)


def get_first_image_path(config):
  input_dir = BASE_DIR / config["local_images"]["dir_path"]
  valid_extensions = tuple(config["local_images"]["valid_extensions"])

  image_paths = [
    path
    for path in input_dir.iterdir()
    if path.is_file() and path.suffix.lower() in valid_extensions
  ]

  if not image_paths:
    raise FileNotFoundError(f"No image found in {input_dir}")

  return sorted(image_paths)[0]


def read_image(image_path):
  image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

  if image is None:
    raise ValueError(f"Failed to read image: {image_path}")

  return image


def validate_roi(image, roi_config):
  x = roi_config["x"]
  y = roi_config["y"]
  w = roi_config["w"]
  h = roi_config["h"]
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


def crop_roi(image, roi_config):
  x = roi_config["x"]
  y = roi_config["y"]
  w = roi_config["w"]
  h = roi_config["h"]
  validate_roi(image, roi_config)
  return image[y : y + h, x : x + w]


def draw_roi_rectangle(image, roi_config):
  result_image = image.copy()

  x = roi_config["x"]
  y = roi_config["y"]
  w = roi_config["w"]
  h = roi_config["h"]
  color = tuple(roi_config["color"])
  thickness = roi_config["thickness"]

  cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)

  return result_image


def save_outputs(config, image_name, roi_image, result_image):
  output_dir = BASE_DIR / "outputs" / config["outputs"]["dir_name"] / image_name
  output_dir.mkdir(parents=True, exist_ok=True)

  roi_path = output_dir / "roi.png"
  result_path = output_dir / "result.png"

  cv2.imwrite(str(roi_path), roi_image)
  cv2.imwrite(str(result_path), result_image)

  return roi_path, result_path


def print_statistics_results(image, roi_image, roi_config, roi_path, result_path):
  image_height, image_width = image.shape[:2]
  roi_height, roi_width = roi_image.shape[:2]

  print(f"原图尺寸：{image_width} x {image_height}")
  print(
    "ROI配置："
    f" x={roi_config['x']}"
    f" y={roi_config['y']}"
    f" w={roi_config['w']}"
    f" h={roi_config['h']}"
  )
  print(f"ROI图片尺寸：{roi_width} x {roi_height}")
  print("ROI校验结果：通过")
  print(f"ROI图片保存路径：{roi_path}")
  print(f"结果图保存路径：{result_path}")


def main():
  config = read_config_json()
  image_path = get_first_image_path(config)
  image = read_image(image_path)

  roi_config = config["roi"]
  roi_image = crop_roi(image, roi_config)
  result_image = draw_roi_rectangle(image, roi_config)

  image_name = image_path.stem
  roi_path, result_path = save_outputs(config, image_name, roi_image, result_image)
  print_statistics_results(image, roi_image, roi_config, roi_path, result_path)


if __name__ == "__main__":
  main()
