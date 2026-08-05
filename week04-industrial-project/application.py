import json
from logging import LoggerAdapter
from typing import Any

from camera import create_image_source
from core import (
    ExitCode,
    NoImageAvailableError,
    PipelineError,
    RunContext,
    RuntimeConfig,
    load_keycap_catalog,
)
from pipelines import run_pipeline
from reporting import OutputWriter


class InspectionApplication:
    """检测应用主类"""

    def __init__(
        self, config: RuntimeConfig, context: RunContext, logger: LoggerAdapter
    ):
        """初始化检测应用实例"""

        self.config = config
        self.context = context
        self.logger = logger
        self.output_writer = OutputWriter(
            self.config.main_config.output, self.context, self.logger
        )

    def run(self) -> ExitCode:
        """完整的检测流程"""

        catalog = load_keycap_catalog(self.config.main_config.input.catalog_path)
        source = create_image_source(self.config, catalog, self.logger)
        with source:
            image_input = source.read()
            if image_input is None:
                raise NoImageAvailableError(source=source.__class__.__name__)
            self._log_image_input(image_input)
        pipeline_output = run_pipeline(self.config, self.context, image_input)
        if pipeline_output is None:
            self.logger.error("流水线执行失败，pipeline_output 为 None")
            raise PipelineError("流水线执行失败，pipeline_output 为 None")
        record = self.output_writer.write(
            image_input=image_input, pipeline_output=pipeline_output
        )
        self.logger.info(
            "检测完成 | image_id=%s | execution_status=%s | inspection_result=%s",
            record.image_id,
            record.execution_status.value,
            record.inspection_result.value,
        )
        return ExitCode.SUCCESS

    def _log_image_input(self, image_input: Any) -> None:
        """统一打印 image_input 的关键信息"""

        def _safe_json(value: Any) -> str:
            """安全地把对象转换成 JSON 字符串"""

            try:
                return json.dumps(value, ensure_ascii=False, default=str)
            except Exception:  # noqa: BLE001
                return str(value)

        # 统一记录基础字段
        self.logger.info(
            "image_shape:%s",
            getattr(getattr(image_input, "image", None), "shape", None),
        )
        self.logger.info("image_id:%s", getattr(image_input, "image_id", None))
        self.logger.info("product_id:%s", getattr(image_input, "product_id", None))
        self.logger.info("batch_id:%s", getattr(image_input, "batch_id", None))
        self.logger.info("captured_at:%s", getattr(image_input, "captured_at", None))
        self.logger.info("source_type:%s", getattr(image_input, "source_type", None))
        self.logger.info("source_path:%s", getattr(image_input, "source_path", None))

        # 只有存在时才打印，避免输出一堆 None
        camera_serial = getattr(image_input, "camera_serial", None)
        if camera_serial is not None:
            self.logger.info("camera_serial:%s", camera_serial)

        camera_parameters = getattr(image_input, "camera_parameters", None)
        if camera_parameters is not None:
            self.logger.info("camera_parameters:%s", _safe_json(camera_parameters))

        metadata = getattr(image_input, "metadata", None)
        if metadata is not None:
            self.logger.info("metadata:%s", _safe_json(metadata))
