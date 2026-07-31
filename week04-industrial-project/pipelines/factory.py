from camera import ImageInput
from core import FeatureNotImplementedError, RunContext, RuntimeConfig

from .traditional import TraditionalPipeline


def run_pipeline(config: RuntimeConfig, context: RunContext, image_input: ImageInput):
    if config.main_config.active_mode == "traditional":
        pipeline = TraditionalPipeline(config, context, image_input)
        return pipeline.run()
    if config.main_config.active_mode == "ocr":
        raise FeatureNotImplementedError("ocr流水线尚未实现")
    if config.main_config.active_mode == "yolo":
        raise FeatureNotImplementedError("yolo流水线尚未实现")
    if config.main_config.active_mode == "combined":
        raise FeatureNotImplementedError("combined流水线尚未实现")
