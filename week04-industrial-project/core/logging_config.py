import logging
import sys
from logging.handlers import RotatingFileHandler

from .config_models import RuntimeConfig
from .context import RunContext
from .paths import resolve_project_path


class RunIdFilter(logging.Filter):
    """给所有的Hanlder拦截的LogRecord注入run)id的Filter"""

    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = self.run_id
        return True


def setup_logging(config: RuntimeConfig, context: RunContext) -> logging.LoggerAdapter:
    """初始化日志"""

    logging_config = config.main_config.logging
    app_name = config.main_config.app.name
    log_level = logging_config.level

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 重复调用，移除并关闭旧Handler
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    # 设置格式器
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(run_id)s | %(message)s"
    )

    handlers: list[logging.Handler] = []
    file_handler_failed = False
    file_failure_error = ""

    run_id_filter = RunIdFilter(context.run_id)

    ## 尝试建立RotatingFileHandler
    if logging_config.file_enabled:
        try:
            log_directory = resolve_project_path(logging_config.directory)
            log_directory.mkdir(parents=True, exist_ok=True)
            log_file_path = log_directory / "application.log"

            file_handler = RotatingFileHandler(
                filename=log_file_path,
                maxBytes=logging_config.max_bytes,
                backupCount=logging_config.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(run_id_filter)
            handlers.append(file_handler)
        except (OSError, ValueError) as exc:
            file_handler_failed = True
            file_failure_error = str(exc)

    # 文件创建失败或日志配置由控制台为True时强制建立控制台Handler
    if logging_config.console or file_handler_failed or not handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # 添加新的Handler并切断父级传播
    for h in handlers:
        root_logger.addHandler(h)

    app_logger = logging.getLogger(app_name)
    app_logger.setLevel(log_level)
    app_logger.propagate = True

    adapter = logging.LoggerAdapter(app_logger, extra={"run_id": context.run_id})

    # 若文件创建失败，输出WARNING并继续启动
    if file_handler_failed:
        adapter.warning(
            f"文件日志初始化失败 (目录: {logging_config.directory}): {file_failure_error}。"
            "已强制降级开启控制台日志继续启动。"
        )

    # 返回LoggerAdapter
    return adapter


def setup_bootstrap_logging() -> logging.LoggerAdapter:
    """创建BOOTSTRAP控制台日志"""

    logger = logging.getLogger("BOOTSTRAP")
    logger.setLevel(logging.INFO)

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(run_id)s | %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logging.LoggerAdapter(logger, extra={"run_id": "BOOTSTRAP"})
