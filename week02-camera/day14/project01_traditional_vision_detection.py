import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def read_config_json():
  """加载JSON配置文件"""
  import json

  config_path = BASE_DIR / "project01_config.json"
  with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
  return config


def read_local_images(config):
  """读取本地图片"""
  import cv2

  images = []
  local_img_cfg = config.get("source", {}).get("local", {})
  dir_path = BASE_DIR / local_img_cfg["dir_path"]
  read_count = local_img_cfg["read_count"]
  valid_extensions = local_img_cfg["valid_extensions"]
  if not dir_path.exists():
    return images
  for index, file_path in enumerate(dir_path.iterdir()):
    if file_path.suffix.lower() in valid_extensions:
      image = cv2.imread(str(file_path))
      if image is not None:
        images.append(
          {"image": image, "source_id": file_path.name, "source_type": "local"}
        )
    if index + 1 == read_count:
      break
  return images


def capture_images(config):
  """相机抓取图片"""
  from camera_common.hik_mvs import HikCamera

  camera_img_cfg = config.get("source", {}).get("camera", {})
  capture_count = camera_img_cfg["capture_count"]
  exposure_time = camera_img_cfg["exposure_time"]
  discard_frames = camera_img_cfg["discard_frames"]
  images = []
  with HikCamera(device_index=0) as camera:
    camera.set_exposure_time(exposure_time)
    camera.discard_frames(discard_frames)
    for index in range(capture_count):
      images.append(
        {
          "image": camera.grab_one_frame(),
          "source_id": f"Camera_{index + 1:02d}",
          "source_type": "camera",
        }
      )
  return images


def load_images(config):
  """获取图片"""
  sys_cfg = config.get("system", {})
  if sys_cfg["input_source"] == "local":
    images = read_local_images(config)
  elif sys_cfg["input_source"] == "camera":
    images = capture_images(config)
  else:
    raise ValueError(f"未知的图片输入来源：{sys_cfg['input_source']}")
  return images


def save_image(path, image):
  """保存图片"""
  import cv2

  saved = cv2.imwrite(str(path), image)
  if not saved:
    raise RuntimeError(f"图片保存失败：{path}")


def save_json(json_path, json_data):
  """保存JSON文件"""
  import json

  if json_data:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump(json_data, f, ensure_ascii=False, indent=2)


def validate_box(box_config, image, name):
  """验证盒子是否越界"""
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
  """裁剪盒子"""
  x = box_config["x"]
  y = box_config["y"]
  w = box_config["w"]
  h = box_config["h"]
  validate_box((x, y, w, h), image, name)
  return image[y : y + h, x : x + w]


def create_template_mode(config):
  """创建固定模板"""
  print("--- 模板创建模式 ---")
  tmpl_cfg = config.get("template", {})
  tmpl_path = BASE_DIR / tmpl_cfg["dir_name"]
  tmpl_path.mkdir(parents=True, exist_ok=True)
  tmpl_file_path = tmpl_path / tmpl_cfg["file_name"]
  tmpl_source_path = tmpl_path / tmpl_cfg["source_name"]
  tmpl_json_path = tmpl_path / tmpl_cfg["meta_name"]
  images = load_images(config)
  if len(images) != 0:
    image = images[0]["image"]
    tmpl_img = crop_box(tmpl_cfg["box"], image, "Template")
    tmpl_h, tmpl_w = tmpl_img.shape[:2]
    json_data = {
      "source": f"{images[0]['source_type']}",
      "template_box": tmpl_cfg["box"],
      "template_size": f"{tmpl_w} x {tmpl_h}",
      "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_image(tmpl_source_path, image)
    save_image(tmpl_file_path, tmpl_img)
    save_json(tmpl_json_path, json_data)
  else:
    raise RuntimeError("图片列表为空!")


def run_match_template(config, roi_img):
  """进行模板比对"""
  import cv2

  tmpl_cfg = config.get("template")
  tmpl_file_path = BASE_DIR / tmpl_cfg["dir_name"] / tmpl_cfg["file_name"]
  tmpl_img = cv2.imread(str(tmpl_file_path), cv2.IMREAD_GRAYSCALE)
  if tmpl_img is None:
    raise RuntimeError(f"模板图片读取失败：{tmpl_file_path}")
  method_map = {
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
  }
  method_str = tmpl_cfg["match"]["method"]
  cv_method = method_map.get(method_str, cv2.TM_SQDIFF_NORMED)
  result = cv2.matchTemplate(roi_img, tmpl_img, cv_method)
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
  is_sqdiff = cv_method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
  tmpl_h, tmpl_w = tmpl_img.shape[:2]
  if is_sqdiff:
    best_score = min_val
    best_loc = min_loc
  else:
    best_score = max_val
    best_loc = max_loc
  return best_score, best_loc, tmpl_w, tmpl_h


def judge_ok_ng(config, best_score):
  """判断NG还是OK"""
  match_cfg = config.get("template", {}).get("match", {})
  threshold = match_cfg["threshold"]
  if best_score >= threshold:
    return "OK", "template score >= threshold"
  else:
    return "NG", "template score < threshold"


def local_box_global_box(config, local_box):
  """roi区域转化为全图区域"""
  local_x, local_y, local_w, local_h = local_box

  global_x = config["roi"]["x"] + local_x
  global_y = config["roi"]["y"] + local_y
  return global_x, global_y, local_w, local_h


def draw_bbox(config, tmpl_global_box, image):
  """绘制ROI框和模板匹配框"""
  import cv2

  draw_cfg = config.get("draw", "")
  roi_thickness = draw_cfg["roi"]["thickness"]
  roi_color = tuple(draw_cfg["roi"]["color"])
  tmpl_thickness = draw_cfg["template"]["thickness"]
  tmpl_color = draw_cfg["template"]["color"]
  roi_cfg = config.get("roi")
  roi_x = roi_cfg["x"]
  roi_y = roi_cfg["y"]
  roi_w = roi_cfg["w"]
  roi_h = roi_cfg["h"]
  t_g_x, t_g_y, t_g_w, t_g_h = tmpl_global_box
  marked_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  cv2.rectangle(
    marked_img,
    (roi_x, roi_y),
    (roi_x + roi_w, roi_y + roi_h),
    roi_color,
    roi_thickness,
    cv2.LINE_AA,
  )
  cv2.rectangle(
    marked_img,
    (t_g_x, t_g_y),
    (t_g_x + t_g_w, t_g_y + t_g_h),
    tmpl_color,
    tmpl_thickness,
    cv2.LINE_AA,
  )
  return marked_img


def build_detect_response(
  config, source, result, best_score, tmpl_local_box, tmpl_global_box, index
):
  """构建比对结果JSON"""
  roi_cfg = config.get("roi")
  sys_cfg = config.get("system", {})
  match_cfg = config.get("template", {}).get("match")
  outputs_cfg = config.get("outputs", {})
  roi_x = roi_cfg["x"]
  roi_y = roi_cfg["y"]
  roi_w = roi_cfg["w"]
  roi_h = roi_cfg["h"]
  t_r_x, t_r_y, t_r_w, t_r_h = tmpl_local_box
  t_g_x, t_g_y, t_g_w, t_g_h = tmpl_global_box
  status, reason = result
  source_id, source_type = source
  json_data = {
    "mode": sys_cfg["mode"],
    "source_id": source_id,
    "source_type": source_type,
    "status": status,
    "reason": reason,
    "best_score": best_score,
    "threshold": match_cfg["threshold"],
    "best_loc_roi": {"x": t_r_x, "y": t_r_y},
    "best_loc_global": {"x": t_g_x, "y": t_g_y},
    "roi": {"x": roi_x, "y": roi_y, "w": roi_w, "h": roi_h},
    "template_size": {"width": t_r_w, "height": t_r_h},
    "outputs": {
      "original": "outputs/original.png",
      "roi": "outputs/roi.png",
      "result": "outputs/result.png",
    },
  }
  if outputs_cfg["use_subfolder"]:
    subfolder_prefix = outputs_cfg["subfolder_prefix"]
    json_data["outputs"] = {
      "original": f"outputs/{subfolder_prefix}_{index + 1:02d}/original.png",
      "roi": f"outputs/{subfolder_prefix}_{index + 1:02d}/roi.png",
      "result": f"outputs/{subfolder_prefix}_{index + 1:02d}/result.png",
    }
  return json_data


def save_outputs(config, index, original_img, roi_img, result_img, json_data):
  """保存图片和JSON文件"""
  outputs_cfg = config.get("outputs", {})
  outputs_path = BASE_DIR / outputs_cfg["base_dir"]
  outputs_path.mkdir(parents=True, exist_ok=True)
  json_name = outputs_cfg["data"]["result_filename"]
  if outputs_cfg["use_subfolder"]:
    subfolder_prefix = outputs_cfg["subfolder_prefix"]
    outputs_path = outputs_path / f"{subfolder_prefix}_{index + 1:02d}"
    outputs_path.mkdir(parents=True, exist_ok=True)
  original_path = outputs_path / "original.png"
  roi_path = outputs_path / "roi.png"
  result_path = outputs_path / "result.png"
  json_path = outputs_path / json_name

  if json_data:
    save_json(json_path, json_data)
  if original_img is not None:
    save_image(original_path, original_img)
  if roi_img is not None:
    save_image(roi_path, roi_img)
  if result_img is not None:
    save_image(result_path, result_img)


def save_summary_json(config, json_data):
  """保存图片和JSON文件"""
  outputs_cfg = config.get("outputs", {})
  outputs_path = BASE_DIR / outputs_cfg["base_dir"]
  outputs_path.mkdir(parents=True, exist_ok=True)
  json_name = outputs_cfg["data"]["summary_filename"]
  json_path = outputs_path / json_name

  if json_data:
    save_json(json_path, json_data)


def build_summary_json(summary_json, json_data):
  if not summary_json:
    summary_json = {
      "total_count": 0,
      "ok_count": 0,
      "ng_count": 0,
      "best_score": {"min": 0.0, "max": 0.0, "mean": 0.0},
      "best_loc_global": {
        "x_min": 0,
        "x_max": 0,
        "x_mean": 0,
        "y_min": 0,
        "y_max": 0,
        "y_mean": 0,
        "x_range": 0,
        "y_range": 0,
      },
      "items": [],
    }
  summary_json["total_count"] += 1
  if json_data["status"] == "OK":
    summary_json["ok_count"] += 1
  if json_data["status"] == "NG":
    summary_json["ng_count"] += 1
  summary_json["items"].append(json_data)
  best_scores = [item["best_score"] for item in summary_json["items"]]
  best_loc_xs = [item["best_loc_global"]["x"] for item in summary_json["items"]]
  best_loc_ys = [item["best_loc_global"]["y"] for item in summary_json["items"]]
  summary_json["best_score"]["max"] = max(best_scores)
  summary_json["best_score"]["min"] = min(best_scores)
  summary_json["best_score"]["mean"] = sum(best_scores) / len(best_scores)
  summary_json["best_loc_global"]["x_max"] = max(best_loc_xs)
  summary_json["best_loc_global"]["x_min"] = min(best_loc_xs)
  summary_json["best_loc_global"]["x_mean"] = sum(best_loc_xs) / len(best_loc_xs)
  summary_json["best_loc_global"]["y_max"] = max(best_loc_ys)
  summary_json["best_loc_global"]["y_min"] = min(best_loc_ys)
  summary_json["best_loc_global"]["y_mean"] = sum(best_loc_ys) / len(best_loc_ys)
  summary_json["best_loc_global"]["x_range"] = max(best_loc_xs) - min(best_loc_xs)
  summary_json["best_loc_global"]["y_range"] = max(best_loc_ys) - min(best_loc_ys)
  return summary_json


def detect_mode(config):
  """正式检测"""
  print("--- 正式检测模式 ---")
  roi_cfg = config.get("roi")
  summary_json = {}
  for index, item in enumerate(load_images(config)):
    roi_img = crop_box(roi_cfg, item["image"], "ROI")
    best_score, best_loc, tmpl_w, tmpl_h = run_match_template(config, roi_img)
    result = judge_ok_ng(config, best_score)
    tmpl_roi_box = (best_loc[0], best_loc[1], tmpl_w, tmpl_h)
    tmpl_global_box = local_box_global_box(config, tmpl_roi_box)
    result_img = draw_bbox(config, tmpl_global_box, item["image"])
    json_data = build_detect_response(
      config,
      (item["source_id"], item["source_type"]),
      result,
      best_score,
      tmpl_roi_box,
      tmpl_global_box,
      index,
    )
    summary_json = build_summary_json(summary_json, json_data)
    save_outputs(config, index, item["image"], roi_img, result_img, json_data)
  save_summary_json(config, summary_json)


def main():
  config = read_config_json()

  sys_cfg = config.get("system", {})
  if sys_cfg["mode"] == "create_template":
    create_template_mode(config)
  elif sys_cfg["mode"] == "detect":
    detect_mode(config)
  else:
    raise ValueError(f"未知的运行模式：{sys_cfg['mode']}")


if __name__ == "__main__":
  main()
