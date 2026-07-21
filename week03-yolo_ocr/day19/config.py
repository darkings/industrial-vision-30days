import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Tuple, List


# ==========================================
# 1. 定义子模块结构 (自底向上)
# ==========================================
class SystemConfig(BaseModel):
  mode: str
  input_source: str
  save_strategy: str


class CameraConfig(BaseModel):
  exposure_time: int
  discard_frames: int
  capture_count: int


class LocalSourceConfig(BaseModel):
  dir_path: str
  valid_extensions: List[str]
  read_count: int


class SourceConfig(BaseModel):
  camera: CameraConfig
  local: LocalSourceConfig


class RoiConfig(BaseModel):
  x: int
  y: int
  w: int
  h: int


class ValidationConfig(BaseModel):
  min_confidence: float = Field(ge=0.0, le=1.0)
  line_count: int
  expected_texts: List[str]


class OCRConfig(BaseModel):
  use_textline_orientation: bool
  enable_mkldnn: bool
  lang: str
  validation: ValidationConfig


class MatchConfig(BaseModel):
  method: str
  threshold: float = Field(ge=0.0, le=1.0)


class BoxConfig(BaseModel):
  x: int
  y: int
  w: int
  h: int


class TemplateConfig(BaseModel):
  enable: bool
  dir_name: str
  source_name: str
  file_name: str
  meta_name: str
  match: MatchConfig
  box: BoxConfig


class FilterConfig(BaseModel):
  enable: bool
  type: str
  ksize: Tuple[int, int]


class BinaryConfig(BaseModel):
  enable: bool
  thresh_val: int
  max_val: int = 255
  inverse: bool
  use_otsu: bool


class PreprocessConfig(BaseModel):
  filter: FilterConfig
  binary: BinaryConfig


class ContourFilterConfig(BaseModel):
  min_area: int
  margin: int
  min_aspect_ratio: float
  max_aspect_ratio: float


class DrawItemConfig(BaseModel):
  thickness: int
  # 强制校验为 3 个整数的元组 (B, G, R)
  color: Tuple[int, int, int]


class DrawConfig(BaseModel):
  contour: DrawItemConfig
  template: DrawItemConfig
  roi: DrawItemConfig
  ocr: DrawItemConfig


class JudgeConfig(BaseModel):
  expected_count: int
  min_area: int
  max_area: int
  min_aspect_ratio: float
  max_aspect_ratio: float


class OutputImagesConfig(BaseModel):
  save_original: bool
  save_roi: bool
  save_result: bool


class OutputDataConfig(BaseModel):
  save_result: bool
  save_summary: bool
  save_rule_result: bool
  result_filename: str
  summary_filename: str
  rule_result_filename: str


class OutputsConfig(BaseModel):
  base_dir: str
  use_subfolder: bool
  subfolder_prefix: str
  images: OutputImagesConfig
  data: OutputDataConfig


# ==========================================
# 2. 定义总配置入口
# ==========================================
class AppConfig(BaseModel):
  system: SystemConfig
  source: SourceConfig
  roi: RoiConfig
  ocr: OCRConfig
  template: TemplateConfig
  preprocess: PreprocessConfig
  contour_filter: ContourFilterConfig
  draw: DrawConfig
  judge: JudgeConfig
  outputs: OutputsConfig


# ==========================================
# 3. 加载与实例化 (单例模式)
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def _load_config() -> AppConfig:
  if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"找不到配置文件: {CONFIG_PATH}")

  with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    raw_yaml = yaml.safe_load(f)

  return AppConfig(**raw_yaml)


# 暴漏给全局的配置对象
cfg = _load_config()
