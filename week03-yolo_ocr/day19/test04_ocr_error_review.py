"""
输入：
*_result.json
*_rule_result.json
输出：
*_error_review.json
建议结构：
{
  "input_image": "...",
  "ocr_result_path": "...",
  "rule_result_path": "...",
  "status": "OK/NG",
  "review_type": "ocr_ok_rule_ng",
  "observations": [],
  "possible_causes": [],
  "next_actions": []
}
判断逻辑先简单做：
如果 status=true：
  review_type = "pass"
  next_actions = ["保留当前 ROI、成像和规则配置"]
如果 status=false，但   ：
  review_type = "ocr_ok_rule_ng"
  possible_causes = ["OCR 识别稳定，但当前图片不符合 expected_texts"]
如果 status=false，且存在低置信度：
  review_type = "low_confidence"
  possible_causes = ["图像模糊、ROI 裁剪、反光或预处理影响 OCR"]
"""

from pathlib import Path
from config import cfg


BASE_DIR = Path(__file__).resolve().parent


def read_base_file_names():
  """
  读取基础文件名
  """
  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  base_names = set()

  for file_path in outputs_dir.glob("*.json"):
    file_name = Path(file_path).stem
    parts = file_name.split("_")
    if len(parts) >= 2:
      base_names.add(f"{parts[0]}_{parts[1]}")

  return sorted(list(base_names))


def load_json_results(file_type="result", file_name=None):
  """
  读取JSON文件
  """
  import json

  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  data_cfg = cfg.outputs.data

  if file_name is None:
    raise RuntimeError(f"文件名称不能为空")

  if file_type == "result":
    file_path = outputs_dir / f"{file_name}_result.json"
  elif file_type == "rule":
    file_path = outputs_dir / f"{file_name}_rule_result.json"
  else:
    raise RuntimeError(f"不支持的文件类型:{file_type}")

  if not outputs_dir.exists() or not file_path.exists():
    raise RuntimeError("读取文件或文件目录不存在")

  try:
    with open(file_path, "r", encoding="utf-8") as f:
      return file_path, json.load(f)
  except json.JSONDecodeError:
    print(f"JSON文件不是合法的JSON格式 路径：{file_path}")
  except Exception as e:
    print(f"JSON文件读取失败：{e} 路径：{file_path}")


def build_review_json(raw_results, rule_results):
  """
  构建reviewJSON数据
  """
  raw_path, raw_result = raw_results
  rule_path, rule_result = rule_results
  status = rule_result["status"]
  is_all_high_confidence = len(
    [d["confidence"] for d in raw_result["detections"] if d["confidence"] >= 0.9]
  ) == len(raw_result["detections"])
  min_conf = cfg.ocr.validation.min_confidence
  low_conf_count = len(
    [d["confidence"] for d in raw_result["detections"] if d["confidence"] < min_conf]
  )
  observations, next_actions, possible_causes = [], [], []

  if status:
    review_type = "pass"
    next_actions = ["保留当前 ROI、成像和规则配置"]
    observations.append("保留当前 ROI、成像和规则配置")
  elif is_all_high_confidence:
    review_type = "ocr_ok_rule_ng"
    possible_causes = ["OCR 识别稳定，但当前图片不符合 expected_texts"]
    observations.append("OCR 识别稳定，但当前图片不符合 expected_texts")
    next_actions = ["确认 expected_texts 是否对应当前图片或产品配方"]
  elif low_conf_count > 0:
    review_type = "low_confidence"
    possible_causes = ["图像模糊、ROI 裁剪、反光或预处理影响 OCR"]
    observations.append("图像模糊、ROI 裁剪、反光或预处理影响 OCR")
    next_actions = ["调整光源、相机参数、ROI裁剪、图片预处理操作"]

  return {
    "input_image": raw_result["input_image"],
    "ocr_result_path": str(raw_path),
    "rule_result_path": str(rule_path),
    "status": "OK" if status else "NG",
    "review_type": review_type,
    "observations": observations,
    "possible_causes": possible_causes,
    "next_actions": next_actions,
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
  outputs_dir = BASE_DIR / cfg.outputs.base_dir
  base_names = read_base_file_names()
  for base_name in base_names:
    raw_results = load_json_results(file_type="result", file_name=base_name)
    rule_results = load_json_results(file_type="rule", file_name=base_name)
    review_json = build_review_json(raw_results, rule_results)
    review_path = outputs_dir / f"{base_name}_error_review.json"
    save_json(review_path, review_json)


if __name__ == "__main__":
  main()
