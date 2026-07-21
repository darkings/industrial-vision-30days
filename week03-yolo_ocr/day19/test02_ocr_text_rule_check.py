from pathlib import Path

from config import cfg


BASE_DIR = Path(__file__).resolve().parent


def load_local_json():
  """
  读取JSON文件
  """
  import json

  json_name = cfg.outputs.data.result_filename
  outputs_dir = BASE_DIR / cfg.outputs.base_dir

  result_jsons = []
  for file_path in outputs_dir.glob(f"*{json_name}"):
    if file_path.name.endswith("_rule_result.json"):
      continue
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        result_jsons.append((file_path, data))
    except json.JSONDecodeError:
      print(f"JSON文件不是合法的JSON格式 路径：{file_path}")
    except Exception as e:
      print(f"JSON文件读取失败：{e} 路径：{file_path}")
  return result_jsons


def extract_recognized_texts_and_confidence(detections):
  """
  根据detections提取文本和置信度
  """
  text_conf_pairs = [
    (item.get("text", ""), item.get("confidence", 0.0)) for item in detections
  ]
  return text_conf_pairs


def judge_ocr_result(text_conf_pairs):
  """
  综合判定图片的OCR结果 OK/NG
  """
  status, reasons = True, []
  line_count_ok, text_match_ok, confidence_ok = True, True, True

  # 效验行数是否正确
  line_count = cfg.ocr.validation.line_count
  if len(text_conf_pairs) != cfg.ocr.validation.line_count:
    line_count_ok = False
    status = False
    reasons.append(f"行数不匹配，期待为{line_count},实际为{len(text_conf_pairs)}")

  # 效验是否有低于最小置信度文本
  min_conf = cfg.ocr.validation.min_confidence
  low_confidence_texts = [text for text, conf in text_conf_pairs if conf < min_conf]
  if len(low_confidence_texts) > 0:
    confidence_ok = False
    status = False
    reasons.append(f"存在置信度小于{min_conf}的文本：{low_confidence_texts}")

  # 效验文本是否与正确文本相同
  expected_texts = cfg.ocr.validation.expected_texts
  extracted_texts = [text for text, _ in text_conf_pairs]
  if expected_texts != extracted_texts:
    text_match_ok = False
    status = False

    missmatches = []
    for index, (actual, expected) in enumerate(zip(extracted_texts, expected_texts)):
      if actual != expected:
        missmatches.append(f"第{index + 1}行,应为{expected},实为{actual}")

    reasons.append(f"文本与期待文本不一致：{','.join(missmatches)}")

  return (line_count_ok, text_match_ok, confidence_ok), status, reasons


def build_rule_result_json_data(
  status, reasons, detections, json_path, image_path, checks
):
  """
  构建效验结果JSON
  """
  recognized_texts = [detect["text"] for detect in detections]
  line_count_ok, text_match_ok, confidence_ok = checks
  return {
    "input_image": str(image_path),
    "ocr_result_path": str(json_path),
    "expected_texts": cfg.ocr.validation.expected_texts,
    "recognized_texts": recognized_texts,
    "min_confidence": cfg.ocr.validation.min_confidence,
    "status": status,
    "reasons": reasons,
    "checks": {
      "line_count_ok": line_count_ok,
      "text_match_ok": text_match_ok,
      "confidence_ok": confidence_ok,
    },
  }


def save_json(path: Path, data: dict):
  """
  JSON 数据保存
  """
  import json

  try:
    with open(path, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
  except Exception as e:
    raise RuntimeError(f"JSON 保存失败: {path}, 错误: {e}")


def main():
  outputs_dir = cfg.outputs.base_dir
  results = load_local_json()
  for file_path, data in results:
    image_path = data.get("input_image", "")
    json_path = BASE_DIR / outputs_dir / f"{Path(image_path).stem}_rule_result.json"
    detections = data.get("detections", [])
    text_conf_pairs = extract_recognized_texts_and_confidence(detections)
    checks, status, reasons = judge_ocr_result(text_conf_pairs)
    rule_result_data = build_rule_result_json_data(
      status, reasons, detections, file_path, image_path, checks
    )
    save_json(json_path, rule_result_data)


if __name__ == "__main__":
  main()
