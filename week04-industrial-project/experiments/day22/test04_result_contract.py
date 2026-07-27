import sys
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.result import (
    ErrorInfo,
    ExecutionStatus,
    InspectionRecord,
    InspectionResult,
    ResultPaths,
    TimingInfo,
    VersionInfo,
)

PROJECT_ROOT_PATH = Path(__file__).resolve().parents[2]


def create_base_payload():
    """生成基础有效字典"""
    return {
        "schema_version": "1.0.0",
        "run_id": "run_20260727_001",
        "image_id": "img_001",
        "batch_id": "batch_01",
        "timestamp": datetime.now().astimezone(),
        "mode": "yolo",
        "versions": VersionInfo(
            app_version="1.0.0", config_version="1.0.0", model_version="v1"
        ),
        "paths": ResultPaths(input_path=Path("data/input.png")),
        "timing": TimingInfo(preprocess_ms=12.5, inference_ms=45.0, total_ms=57.5),
        "reason_codes": ["PASS_CODE"],
        "message": "Inspection completed successfully.",
    }


def test_valid_cmbinations():
    """测试有效性组合"""
    outputs_dir = PROJECT_ROOT_PATH / "outputs" / "DAY22_RESULT_CONTRACT"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    valid_cases = [
        (ExecutionStatus.SUCCESS, InspectionResult.OK, None, "success_ok.json"),
        (ExecutionStatus.SUCCESS, InspectionResult.NG, None, "success_ng.json"),
        (
            ExecutionStatus.SUCCESS,
            InspectionResult.UNKNOWN,
            None,
            "success_unknown.json",
        ),
        (
            ExecutionStatus.ERROR,
            InspectionResult.UNKNOWN,
            ErrorInfo(
                error_type="TimeoutError",
                stage="inference",
                message="GPU inference timeout after 5000ms",
                recoverable=True,
            ),
            "error_unknown.json",
        ),
    ]

    for status, result, err, filename in valid_cases:
        data = create_base_payload()
        data["execution_status"] = status
        data["inspection_result"] = result
        data["error"] = err
        if result == InspectionResult.NG:
            data["reason_codes"] = ["DEFECT_SCRATCH"]
            data["message"] = "Defect scratch detected."
        elif result == InspectionResult.UNKNOWN and status == ExecutionStatus.SUCCESS:
            data["reason_codes"] = ["LOW_CONFIDENCE"]
            data["message"] = "Detection confidence below threshold."
        elif status == ExecutionStatus.ERROR:
            data["reason_codes"] = ["SYSTEM_ERROR"]
            data["message"] = "System error occurred during inference."

        record = InspectionRecord(**data)

        file_path = outputs_dir / filename
        file_path.write_text(record.model_dump_json(indent=4), encoding="utf-8")


def test_invalid_combinations():
    """测试无效性组合"""
    invalid_cases = [
        (
            "ERROR + OK",
            ExecutionStatus.ERROR,
            InspectionResult.OK,
            None,
            ["SYS_ERR"],
        ),
        (
            "ERROR + NG",
            ExecutionStatus.ERROR,
            InspectionResult.NG,
            None,
            ["SYS_ERR"],
        ),
        (
            "ERROR + UNKNOWN且没有error",
            ExecutionStatus.ERROR,
            InspectionResult.UNKNOWN,
            None,
            ["SYS_ERR"],
        ),
        (
            "SUCCESS + OK但带有error",
            ExecutionStatus.SUCCESS,
            InspectionResult.OK,
            ErrorInfo(
                error_type="DummyError",
                stage="test",
                message="Should not exist",
                recoverable=False,
            ),
            ["PASS_CODE"],
        ),
        ("空reason_codes", ExecutionStatus.SUCCESS, InspectionResult.OK, None, []),
    ]
    for name, status, result, err, reasons in invalid_cases:
        data = create_base_payload()
        data["execution_status"] = status
        data["inspection_result"] = result
        data["error"] = err
        data["reason_codes"] = reasons

        try:
            InspectionRecord(**data)
        except ValidationError:
            print(f"[验证成功捕获] {name} 成功触发 ValidationError 并拦截。")
        else:
            # 在没有触发 ValidationError 时主动抛出 AssertionError
            raise AssertionError(
                f"未捕获 ValidationError！无效组合 [{name}] 竟然通过了校验！"
            )


def main():
    test_valid_cmbinations()
    test_invalid_combinations()


if __name__ == "__main__":
    main()
