import logging

from types import FrameType
from typing import cast

from loguru import logger


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_loguru_logging_intercept(modules=()):
    root_logger = logging.getLogger()
    logging.basicConfig(handlers=[InterceptHandler()], level=root_logger.level)  # noqa
    for logger_name in modules:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=mod_logger.level)]
        mod_logger.propagate = False
