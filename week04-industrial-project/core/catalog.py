from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.config import load_yaml
from core.exceptions import CatalogError, ProductNotFoundError
from core.paths import resolve_project_path


class KeycapProduct(BaseModel):
    """键帽单品模型，用于定义单个键帽的基本规格和标识信息。"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    product_id: str = Field(..., description="键帽单品的唯一编号")
    legend: str = Field(..., description="键帽表面字符")
    size_u: float = Field(..., description="键帽的标准尺寸宽度")

    @model_validator(mode="after")
    def validate_keycap_product(self) -> "KeycapProduct":
        if not self.legend.strip():
            raise ValueError("键帽字符不能为空")
        if not self.product_id.strip():
            raise ValueError("产品编号不能为空")
        if self.size_u <= 0:
            raise ValueError("键帽的宽度不能小于等于 0U")
        return self


class KeycapCatalog(BaseModel):
    """键帽套装模型，用于管理一组关联的键帽产品列表"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    set_id: str = Field(..., description="键帽套装的唯一标识符")
    products: list[KeycapProduct] = Field(..., description="套装内包含的键帽单品列表")

    @model_validator(mode="after")
    def validate_keycap_catalog(self) -> "KeycapCatalog":
        if not self.set_id.strip():
            raise ValueError("套装标识 (set_id) 不能为空")
        if not self.products:
            raise ValueError("产品列表 (products) 不能为空")
        product_ids = [p.product_id for p in self.products]
        if len(set(product_ids)) != len(product_ids):
            raise ValueError("产品列表中存在重复的产品标识 (product_id)")

        return self

    def get_product(self, product_id: str) -> KeycapProduct:
        for product in self.products:
            if product.product_id == product_id:
                return product

        raise ProductNotFoundError(product_id=product_id)


def load_keycap_catalog(catalog_path: str | Path) -> KeycapCatalog:
    """加载键盘套装"""
    try:
        catalog_path = resolve_project_path(catalog_path)
        catalog_config = load_yaml(catalog_path)
        return KeycapCatalog.model_validate(catalog_config)
    except (ValueError, OSError, TypeError) as exc:
        raise CatalogError(f"创建KeycapCatalog失败：{exc}") from exc
