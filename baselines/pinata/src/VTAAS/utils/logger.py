import logging
import os
import time
from typing import final, override


@final
class ElapsedTimeFormatter(logging.Formatter):
    """Custom formatter to display elapsed time in hh:mm:ss format."""

    def __init__(
        self,
        start_time: float,
        fmt: str = "\n%(elapsed_time)s - %(name)s - %(levelname)s - %(message)s",
    ):
        super().__init__(fmt)
        self.start_time = start_time

    @override
    def format(self, record: logging.LogRecord) -> str:
        elapsed_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        record.elapsed_time = f"{hours:02}:{minutes:02}:{seconds:02}"
        return super().format(record)


def get_logger(name: str, start_time: float, output_folder: str) -> logging.Logger:
    """Configure and return a logger instance with elapsed time formatting."""
    logger = logging.getLogger(name)

    if logger.handlers:
        raise ValueError(f"\n\nThe logger {name} should not already exist!")

    os.makedirs(output_folder, exist_ok=True)
    formatter = ElapsedTimeFormatter(start_time)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log_file = os.path.join(output_folder, "execution.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')  # <--- 修正行
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    return logger
