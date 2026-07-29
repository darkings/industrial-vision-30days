from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ImageInput(BaseModel):
    """图像输入数据模型，用于封装并校验从不同来源采集的图像及其元数据。"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )
    image: np.ndarray = Field(..., description="图像数据矩阵，必须为非空的 NumPy 数组")
    image_id: str = Field(..., description="图像的唯一标识符")
    product_id: str = Field(..., description="关联的产品编号")
    batch_id: str = Field(..., description="生产批次编号")
    captured_at: datetime = Field(
        ..., description="图像采集的带时区时间戳（必须包含时区信息）"
    )
    source_type: Literal["image", "directory", "camera"] = Field(
        ..., description="图像来源类型"
    )
    source_path: Path | None = Field(
        default=None, description="源文件或源目录的存储路径，可选项"
    )
    camera_serial: str | None = Field(
        default=None, description="采集相机的序列号，仅在相机模式下可选"
    )
    camera_parameters: dict[str, Any] = Field(
        default_factory=dict, description="相机采集时的参数字典"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="自定义扩展元数据"
    )

    @model_validator(mode="after")
    def validate_image_input_logic(self) -> "ImageInput":
        if not isinstance(self.image, np.ndarray):
            raise TypeError("输入的图像数据类型必须为 np.ndarray")
        if self.image.size == 0:
            raise ValueError("输入的图像为空，未包含有效的像素数据")
        if not self.image_id.strip():
            raise ValueError("图像标识不能为空")
        if not self.product_id.strip():
            raise ValueError("产品编号不能为空")
        if not self.batch_id.strip():
            raise ValueError("生产批次不能为空")
        is_aware = (
            self.captured_at.tzinfo is not None
            and self.captured_at.tzinfo.utcoffset(self.captured_at) is not None
        )
        if not is_aware:
            raise ValueError("采集时间必须带有有效的时区信息")

        return self


class ImageSource(ABC):
    """图像来源抽象基类"""

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def read(self) -> ImageInput | None:
        pass

    @abstractmethod
    def close(self):
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
