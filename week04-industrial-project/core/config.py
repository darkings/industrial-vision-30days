from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .config_models import (
    MODE_CONFIG_MODELS,
    MainConfig,
    RuntimeConfig,
    StrictConfigModel,
)
from .exceptions import ConfigError
from .paths import PROJECT_ROOT_PATH, resolve_project_path


def load_yaml(config_path: Path) -> dict[str, Any]:
    """加载yaml文件"""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"读取YAML配置失败，配置文件不存在{config_path}")
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"读取YAML配置失败，当前路径不是一个文件{config_path}")
    if Path(config_path).suffix.lower() != ".yaml":
        raise ValueError(f"读取YAML配置失败，配置文件不是一个YAML文件{config_path}")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"读取YAML配置失败，YAML语法错误：{config_path}") from exc
    except OSError as exc:
        raise ValueError(f"读取YAML配置失败，文件无法打开：{config_path}") from exc

    if data is None:
        raise ValueError(f"读取YAML配置失败，YAML文件内容为空：{config_path}")

    if not isinstance(data, dict):
        raise TypeError(f"读取YAML配置失败，YAML文件内容不是一个字典：{config_path}")

    return data


def load_main_config() -> MainConfig:
    """加载主配置文件"""
    main_config_path = PROJECT_ROOT_PATH / "configs" / "main.yaml"

    try:
        raw_dict = load_yaml(config_path=main_config_path)
        config = MainConfig.model_validate(raw_dict)
        return config
    except (ValueError, ValidationError) as exc:
        raise ConfigError(f"配置文件格式格式或数值不符合业务规则要求：{exc}") from exc


def load_mode_config(main_config: MainConfig) -> StrictConfigModel:
    """读取模式配置文件"""
    active_mode = main_config.active_mode
    active_mode_path = resolve_project_path(
        getattr(main_config.mode_configs, active_mode)
    )

    try:
        raw_dict = load_yaml(active_mode_path)
        acitve_config = MODE_CONFIG_MODELS[active_mode]
        config = acitve_config.model_validate(raw_dict)
        return config
    except (ValueError, ValidationError) as exc:
        raise ConfigError(f"配置文件格式格式或数值不符合业务规则要求：{exc}") from exc


def load_config() -> RuntimeConfig:
    """加载运行配置"""

    try:
        main_config = load_main_config()
        mode_config = load_mode_config(main_config)
        runtime_config = {"main_config": main_config, "mode_config": mode_config}
        config = RuntimeConfig.model_validate(runtime_config)
        return config
    except (ValueError, TypeError, FileNotFoundError) as exc:
        raise ConfigError(f"配置文件格式格式或数值不符合业务规则要求：{exc}") from exc
