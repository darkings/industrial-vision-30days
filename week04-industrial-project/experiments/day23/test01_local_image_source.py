import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera.local_source import LocalImageSource
from core.catalog import load_keycap_catalog
from core.config import load_config


def main():

    config = load_config()
    catalog = load_keycap_catalog(config.main_config.input.catalog_path)
    product = catalog.get_product(config.main_config.input.product_id)
    assert product is not None, (
        f"ProductID{config.main_config.input.product_id}在catalog没有找到"
    )
    with LocalImageSource(
        image_path=config.main_config.input.image_path,
        product=product,
        batch_id=config.main_config.input.batch_id,
        allowed_extensions=config.main_config.input.allowed_extensions,
    ) as source:
        source.open()
        image_input = source.read()
        assert image_input is not None, "第一次读取失败"
        image_input2 = source.read()
        assert image_input2 is None, "单词读取，第二次返回None."
        source.close()
        source.close()


if __name__ == "__main__":
    main()
