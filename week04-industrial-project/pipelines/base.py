from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np
from core import InspectionRecord


@dataclass(slots=True)
class PipelineOutput:
    record: InspectionRecord
    annotated_image: np.ndarray | None
    debug_images: dict[str, np.ndarray] = field(default_factory=dict)


class BasePipeline(ABC):
    @abstractmethod
    def run(self) -> PipelineOutput:
        raise NotImplementedError
