import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core import load_yaml

BASE_DIR = Path(__file__).resolve().parent


def test_01(yolo_01_path):
    """正确用例通过"""
    try:
        config = load_yaml(yolo_01_path)
        assert isinstance(config, dict)
        assert config["mode"] == "yolo"
        assert config["config_version"] == "1.0.0"
    except yaml.YAMLError as e:
        print(f"错误：{e}")


def test_02(yolo_02_path):
    """错误用例：文件不存在"""
    try:
        config = load_yaml(yolo_02_path)
        print(config)
    except FileNotFoundError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期文件不存在失败，但验证成功")


def test_03(yolo_03_path):
    """错误用例：空文件"""
    try:
        config = load_yaml(yolo_03_path)
        print(config)
    except ValueError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期空文件失败，但验证成功")


def test_04(yolo_04_path):
    """错误用例：根节点为列表"""
    try:
        config = load_yaml(yolo_04_path)
        print(config)
    except TypeError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期根节点为列表失败，但验证成功")


def test_05(yolo_05_path):
    """错误用例：语法错误"""
    try:
        config = load_yaml(yolo_05_path)
        print(config)
    except ValueError as e:
        print(f"错误：{e}")
    else:
        raise AssertionError("预期语法错误失败，但验证成功")


def main():
    yolo_01_path = BASE_DIR / "yolo_01.yaml"
    yolo_02_path = BASE_DIR / "yolo_02.yaml"
    yolo_03_path = BASE_DIR / "yolo_03.yaml"
    yolo_04_path = BASE_DIR / "yolo_04.yaml"
    yolo_05_path = BASE_DIR / "yolo_05.yaml"
    test_01(yolo_01_path)
    test_02(yolo_02_path)
    test_03(yolo_03_path)
    test_04(yolo_04_path)
    test_05(yolo_05_path)


if __name__ == "__main__":
    main()
