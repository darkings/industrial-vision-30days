from core.config import load_config
from core.context import create_run_context
from core.logging_config import setup_bootstrap_logging, setup_logging


def main() -> int:
    """程序主入口"""
    logger = setup_bootstrap_logging()
    logger.info("程序正在启动，开始解析配置文件")
    try:
        config = load_config()
    except Exception:
        logger.exception("读取配置文件失败")
        return 1
    try:
        context = create_run_context(config)
        logger = setup_logging(config, context)
    except Exception:
        logger.exception("获取程序上下文失败")
        return 1
    logger.info("配置加载成功，系统日志初始化完毕")
    logger.info(f"app_version：{config.main_config.app.version}")
    logger.info(f"active_mode：{config.main_config.active_mode}")
    logger.info(f"mode_config_type：{type(config.mode_config).__name__}")
    logger.info(f"run_id：{context.run_id}")
    logger.info(f"output_dir：{context.output_dir}")
    logger.info(f"report_dir：{context.report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
