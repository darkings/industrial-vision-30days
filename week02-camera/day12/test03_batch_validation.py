import json

from camera_common.hik_mvs import HikCamera
from pathlib import Path
import detection_pipeline as dp

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
  valid_extensions = config["local_images"]["valid_extensions"]
  if not dir_path.exists():
    return images
  for file_path in dir_path.iterdir():
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append({"tag": file_path.name, "image": image})
  return images


def capture_image(config):
  """获取图像

  Returns:
      image: 图像数组
  """
  capture_count = config["camera"]["capture_count"]
  exposure_time = config["camera"]["exposure_time"]
  discard_frames = config["camera"]["discard_frames"]
  images = []
  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(exposure_time)
    camera.discard_frames(discard_frames)
    for index in range(capture_count):
      images.append({"tag": index + 1, "image": camera.grab_one_frame()})
  return images


def save_single_outputs(config, index, image, gray, blur, binary, result, json_data):
  """保存结果

  Args:
      image (ndarray): 原图
      gray (ndarray): 灰度图
      blur (ndarray): 高斯滤波图
      binary (ndarray): 二值图
      result (ndarray): 标注结果图
      json_data (JSON): 结果JSON
  """

  dir_name = config["outputs"]["dir_name"]
  sample_prefix = config["outputs"]["sample_prefix"]

  OUTPUTS_DIR = BASE_DIR / "outputs" / dir_name / f"{sample_prefix}_{index + 1:03d}"
  OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
  original_path = OUTPUTS_DIR / "original.png"
  gray_path = OUTPUTS_DIR / "gray.png"
  blur_path = OUTPUTS_DIR / "blur.png"
  binary_path = OUTPUTS_DIR / "binary.png"
  result_path = OUTPUTS_DIR / "result.png"
  json_path = OUTPUTS_DIR / "detection_result.json"

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)
  if image is not None:
    dp.save_image(original_path, image)
  if gray is not None:
    dp.save_image(gray_path, gray)
  if blur is not None:
    dp.save_image(blur_path, blur)
  if binary is not None:
    dp.save_image(binary_path, binary)
  if result is not None:
    dp.save_image(result_path, result)


def update_summary_json(config, status, single_json):
  dir_name = config["outputs"]["dir_name"]
  summary_filename = config["outputs"]["summary_filename"]
  summary_path = BASE_DIR / "outputs" / dir_name / summary_filename
  summary_path.parent.mkdir(parents=True, exist_ok=True)
  summary_path.touch(exist_ok=True)

  with open(summary_path, "r+", encoding="utf-8") as f:
    content = f.read()
    if not content.strip():
      data = {"total": 0, "ok_count": 0, "ng_count": 0, "items": [], "config": config}
    else:
      data = json.loads(content)

    single_json.pop("config", None)
    data["total"] += 1
    if status == "OK":
      data["ok_count"] += 1
    else:
      data["ng_count"] += 1
    data["items"].append(single_json)

    f.seek(0)
    f.truncate()
    json.dump(data, f, indent=2, ensure_ascii=False)


def reset_output_dir(config):
  """重置输出目录

  Args:
      config (JSON): 配置
  """
  dir_name = config["outputs"]["dir_name"]
  summary_filename = config["outputs"]["summary_filename"]
  summary_path = BASE_DIR / "outputs" / dir_name / summary_filename
  if summary_path.exists():
    summary_path.unlink()


def main():
  config = read_config_json()
  reset_output_dir(config)

  run_mode = config["run_mode"]
  if run_mode == "local":
    images = read_local_images(config)
  else:
    images = capture_image(config)

  for index, item in enumerate(images):
    tag = item["tag"]
    image = item["image"]
    gray, blur, binary, result, single_json, status = dp.run_detection_pipeline(
      config, tag, image
    )
    save_single_outputs(config, index, image, gray, blur, binary, result, single_json)
    update_summary_json(config, status, single_json)


if __name__ == "__main__":
  main()
