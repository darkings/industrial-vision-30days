import time
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any

import cv2
import numpy as np
from camera import ImageInput
from core import (
    INSPECTION_SCHEMA_VERSION,
    ExecutionStatus,
    InspectionRecord,
    InspectionResult,
    ModeConfigTypeError,
    ResultPaths,
    RunContext,
    RuntimeConfig,
    SizeProfileNotFoundError,
    TimingInfo,
    TraditionalConfig,
    VersionInfo,
)
from cv2.typing import MatLike

from .base import BasePipeline, PipelineOutput


class TraditionalPipeline(BasePipeline):
    """传统视觉检测类"""

    def __init__(
        self, config: RuntimeConfig, context: RunContext, image_input: ImageInput
    ):
        """初始化"""

        if not isinstance(config.mode_config, TraditionalConfig):
            raise ModeConfigTypeError(
                f"TraditionalPipeline 只能接收 TraditionalConfig，"
                f"实际收到：{type(config.mode_config).__name__}"
            )

        self.context = context
        self.config = config
        self.mode_config = config.mode_config
        self.image_input = image_input
        self.image, size_u = self._process_image_input()
        self.profile_key = f"{size_u:.1f}u"

        size_profile = self.mode_config.rules.size_profiles.get(self.profile_key)
        if size_profile is None:
            raise SizeProfileNotFoundError(size_u)
        self.size_profile = size_profile

    def run(self) -> PipelineOutput:
        """运行传统视觉检测"""

        t_start = time.perf_counter()
        threshold, binary_image, morphology_image = self._preprocess_image()
        t_preprocess_end = time.perf_counter()
        contours, detections = self._measure_contour_metrics(image=morphology_image)
        execution_status, inspection_result, reason_codes = self._evaluate_ok_ng(
            detections=detections
        )
        t_inference_end = time.perf_counter()

        preprocess_ms = (t_preprocess_end - t_start) * 1000
        inference_ms = (t_inference_end - t_preprocess_end) * 1000
        total_ms = preprocess_ms + inference_ms
        timing = TimingInfo(
            preprocess_ms=preprocess_ms,
            inference_ms=inference_ms,
            total_ms=total_ms,
        )
        record: InspectionRecord = self._build_inspection_record(
            threshold=int(threshold),
            detections=detections,
            contours=contours,
            timing=timing,
            execution_status=execution_status,
            inspection_result=inspection_result,
            reason_codes=reason_codes,
        )

        annotated_image = self._generate_debug_artifacts(record)
        debug_images = {"binary": binary_image, "morphology": morphology_image}
        return PipelineOutput(
            record, annotated_image=annotated_image, debug_images=debug_images
        )

    def _process_image_input(self):
        """接收ImageInput"""

        return self.image_input.image, float(self.image_input.metadata["size_u"])

    def _preprocess_image(self) -> tuple[float, np.ndarray, np.ndarray]:
        """灰度化、滤波、阈值分割、形态学处理图片"""

        processing_config = self.mode_config.processing
        if len(self.image.shape) == 2 or (
            len(self.image.shape) == 3 and self.image.shape[2] == 1
        ):
            gray_image = self.image.copy()
        else:
            gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        kernel = (processing_config.blur_kernel,) * 2
        gaussian_image = cv2.GaussianBlur(gray_image, kernel, 0)
        if processing_config.invert:
            threshold_method = (
                cv2.THRESH_BINARY_INV
                if processing_config.threshold_method == "fixed"
                else cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )
        else:
            threshold_method = (
                cv2.THRESH_BINARY
                if processing_config.threshold_method == "fixed"
                else cv2.THRESH_BINARY | cv2.THRESH_OTSU
            )
            fixed_threshold = 0.0
        if processing_config.threshold_method == "fixed":
            if processing_config.fixed_threshold is None:
                raise ValueError("fixed 阈值模式下 fixed_threshold 不能为空")
            fixed_threshold = processing_config.fixed_threshold
        else:
            fixed_threshold = 0.0
        threshold, binary_image = cv2.threshold(
            gaussian_image, fixed_threshold, 255, threshold_method
        )
        morphology_kernel_size = (processing_config.morphology_kernel,) * 2
        morphology_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, morphology_kernel_size
        )
        morphology_type = (
            cv2.MORPH_OPEN
            if processing_config.morphology_type == "open"
            else cv2.MORPH_CLOSE
        )
        morphology_image = cv2.morphologyEx(
            binary_image, morphology_type, morphology_kernel
        )
        return threshold, binary_image, morphology_image

    def _measure_contour_metrics(
        self, image: np.ndarray
    ) -> tuple[Sequence[MatLike], list[dict[str, Any]]]:
        """查找轮廓并测量面积、位置、宽高和宽高比"""

        contours, _ = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        detections: list[dict[str, Any]] = []
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            area_ok = (
                self.size_profile.min_area is None or area >= self.size_profile.min_area
            ) and (
                self.size_profile.max_area is None or area <= self.size_profile.max_area
            )

            aspect_ratio_ok = (
                self.size_profile.min_aspect_ratio is None
                or aspect_ratio >= self.size_profile.min_aspect_ratio
            ) and (
                self.size_profile.max_aspect_ratio is None
                or aspect_ratio <= self.size_profile.max_aspect_ratio
            )
            if area_ok and aspect_ratio_ok:
                center_x = (x + (x + w)) / 2
                center_y = (y + (y + h)) / 2
                aspect_ratio = w / h
                center_offset_x = center_x - self.mode_config.rules.expected_center_x
                center_offset_y = center_y - self.mode_config.rules.expected_center_y
                detections.append(
                    {
                        "bbox": [x, y, w, h],
                        "area": area,
                        "center": [int(center_x), int(center_y)],
                        "aspect_ratio": aspect_ratio,
                        "center_offset_x": int(center_offset_x),
                        "center_offset_y": int(center_offset_y),
                    }
                )
        return contours, detections

    def _evaluate_ok_ng(
        self, detections: list[dict[str, Any]]
    ) -> tuple[ExecutionStatus, InspectionResult, list[str]]:
        """根据配置判断 OK/NG"""

        execution_status = ExecutionStatus.SUCCESS
        inspection_result = InspectionResult.OK
        reason_codes: list[str] = []
        expected_count = self.mode_config.rules.expected_count
        center_tolerance_px = self.mode_config.rules.center_tolerance_px
        if len(detections) != expected_count:
            execution_status = ExecutionStatus.SUCCESS
            inspection_result = InspectionResult.NG
            reason_codes.append("COUNT_MISMATCH")
        for contour in detections:
            if (
                abs(contour["center_offset_x"]) > center_tolerance_px
                or abs(contour["center_offset_y"]) > center_tolerance_px
            ):
                execution_status = ExecutionStatus.SUCCESS
                inspection_result = InspectionResult.NG
                reason_codes.append("CENTER_OUT_OF_TOLERANCE")
        if inspection_result != InspectionResult.NG:
            execution_status = ExecutionStatus.SUCCESS
            inspection_result = InspectionResult.OK
            if not reason_codes:
                reason_codes.append("TRADITIONAL_OK")
        return execution_status, inspection_result, reason_codes

    def _build_inspection_record(
        self,
        threshold: int,
        detections: list[dict[str, Any]],
        contours: Sequence[MatLike],
        timing: TimingInfo,
        execution_status: ExecutionStatus,
        inspection_result: InspectionResult,
        reason_codes: list[str],
    ):
        """生成统一 InspectionRecord"""

        image_height, image_width = self.image.shape[:2]
        image_center_x = image_width // 2
        image_center_y = image_height // 2
        cn_tz = timezone(timedelta(hours=8))
        measurements = {
            "threshold_used": threshold,
            "raw_contour_count": len(contours),
            "detected_count": len(detections),
            "expected_count": self.mode_config.rules.expected_count,
            "size_profile": self.profile_key,
            "image_center": [image_center_x, image_center_y],
            "expected_center": [
                self.mode_config.rules.expected_center_x,
                self.mode_config.rules.expected_center_y,
            ],
            "objects": detections,
        }
        return InspectionRecord(
            schema_version=INSPECTION_SCHEMA_VERSION,
            run_id=self.context.run_id,
            image_id=self.image_input.image_id,
            batch_id=self.image_input.batch_id,
            timestamp=datetime.now(cn_tz),
            mode=self.config.mode_config.mode,
            execution_status=execution_status,
            inspection_result=inspection_result,
            reason_codes=reason_codes,
            versions=VersionInfo(
                app_version=self.config.main_config.app.version,
                config_version=self.config.mode_config.config_version,
                model_version=None,
            ),
            measurements=measurements,
            message="传统视觉检测完成",
            paths=ResultPaths(input_path=self.image_input.source_path),
            timing=timing,
        )

    def _generate_debug_artifacts(self, record: InspectionRecord) -> np.ndarray | None:
        """生成标注图和必要的调试图"""

        if len(self.image.shape) == 2 or self.image.shape[2] == 1:
            annotated_image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        else:
            annotated_image = self.image.copy()

        # 绘制检测框
        detections: list[dict[str, Any]] = record.measurements.get("objects", [])
        for detect in detections:
            x, y, w, h = detect.get("bbox", [])
            area = detect.get("area", 0.0)
            aspect_ratio = detect.get("aspect_ratio", 0.0)
            cv2.rectangle(
                annotated_image, (x, y), (x + w, y + h), (0, 255, 255), 1, cv2.LINE_AA
            )

            cv2.putText(
                annotated_image,
                f"Area:{area} aspect_ratio:{aspect_ratio}",
                (x, max(y - 15, 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                cv2.LINE_AA,
            )

        # 绘制中心点
        image_center_x, image_center_y = record.measurements.get("image_center", [])
        cv2.drawMarker(
            annotated_image,
            (image_center_x, image_center_y),
            (255, 0, 0),
            cv2.MARKER_CROSS,
            30,
            1,
            cv2.LINE_AA,
        )

        # 绘制示教中心点
        expected_center_x, expected_center_y = record.measurements.get(
            "expected_center", []
        )
        cv2.drawMarker(
            annotated_image,
            (expected_center_x, expected_center_y),
            (0, 255, 0),
            cv2.MARKER_CROSS,
            30,
            1,
            cv2.LINE_AA,
        )

        # 绘制状态原因
        cv2.rectangle(
            annotated_image,
            (0, 0),
            (image_center_x * 2, 40),
            (64, 64, 64),
            -1,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated_image,
            f"Status:{record.inspection_result} Reasons:{','.join(record.reason_codes)}",
            (10, 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0)
            if record.inspection_result == InspectionResult.OK
            else (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

        return annotated_image
