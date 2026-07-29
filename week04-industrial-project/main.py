from application import InspectionApplication
from core.config import load_config
from core.context import create_run_context
from core.exceptions import InspectionError
from core.exit_codes import ExitCode
from core.logging_config import setup_bootstrap_logging, setup_logging


def _log_program_exit(logger, exit_code: ExitCode) -> int:
    log_method = logger.info if exit_code == ExitCode.SUCCESS else logger.error
    log_method(
        "程序结束 | exit_code=%d | exit_name=%s ", int(exit_code), exit_code.name
    )
    return int(exit_code)


def main() -> int:
    """程序主入口"""
    logger = setup_bootstrap_logging()
    logger.info("程序正在启动，开始解析配置文件")
    try:
        config = load_config()
        context = create_run_context(config)
        logger = setup_logging(config, context)
        logger.info("配置加载成功，系统日志初始化完毕")
        logger.info(f"app_version：{config.main_config.app.version}")
        logger.info(f"active_mode：{config.main_config.active_mode}")
        logger.info(f"mode_config_type：{type(config.mode_config).__name__}")
        logger.info(f"run_id：{context.run_id}")
        logger.info(f"output_dir：{context.output_dir}")
        logger.info(f"report_dir：{context.report_dir}")
        application = InspectionApplication(config, context, logger)
        exit_code = application.run()
    except InspectionError as exc:
        logger.error(
            "程序运行失败 | exit_code=%d | exit_name=%s | reason=%s",
            int(exc.exit_code),
            exc.exit_code.name,
            exc,
        )
        exit_code = exc.exit_code
    except Exception as exc:
        logger.exception(
            "程序运行失败 | exit_code=%d | exit_name=%s | reason=%s",
            int(ExitCode.UNEXPECTED_ERROR),
            ExitCode.UNEXPECTED_ERROR.name,
            exc.__class__.__name__,
        )
        exit_code = ExitCode.UNEXPECTED_ERROR
    return _log_program_exit(logger, exit_code=exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
