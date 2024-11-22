import logging
import os
from typing import Dict

from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO)


class LoggingManager:
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.current_log_dir = ""
        self.use_stdout = True
        self.rich_handler = RichHandler(
            show_time=bool(os.environ.get("LLM4RTL_LOG_TIME", False)),
            show_path=bool(os.environ.get("LLM4RTL_LOG_PATH", False)),
        )
        self.rich_handler.setLevel(logging.DEBUG)

    def get_logger(self, name: str) -> logging.Logger:
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Add the handler to the logger
        logger.addHandler(self.rich_handler)
        logger.propagate = False

        # Store the logger in our dictionary
        self.loggers[name] = logger

        return logger

    def set_log_dir(self, new_dir: str) -> None:
        if self.current_log_dir == new_dir:
            return
        self.current_log_dir = new_dir

        # Ensure the new directory exists
        os.makedirs(self.current_log_dir, exist_ok=True)

        if not self.use_stdout:
            self._update_handlers()

    def switch_to_file(self) -> None:
        if not self.use_stdout:
            return
        self.use_stdout = False
        if self.current_log_dir:
            self._update_handlers()

    def switch_to_stdout(self) -> None:
        if self.use_stdout:
            return
        self.use_stdout = True
        self._update_handlers()

    def _update_handlers(self) -> None:
        assert self.current_log_dir and os.path.isdir(self.current_log_dir)

        formatter = logging.Formatter(
            "[%(asctime)s - %(name)s - %(levelname)s] %(message)s"
        )

        if self.use_stdout:
            for _, logger in self.loggers.items():
                # Remove existing handlers
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)
                logger.addHandler(self.rich_handler)
            return

        unified_log_file = os.path.join(self.current_log_dir, f"mage_rtl_total.log")
        if os.path.exists(unified_log_file):
            os.remove(unified_log_file)
        unified_file_handler = logging.FileHandler(unified_log_file)
        unified_file_handler.setLevel(logging.DEBUG)
        unified_file_handler.setFormatter(formatter)

        for name, logger in self.loggers.items():
            # Remove existing handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Add new handler
            new_log_file = os.path.join(self.current_log_dir, f"{name}.log")
            if os.path.exists(new_log_file):
                os.remove(new_log_file)
            new_handler = logging.FileHandler(new_log_file)
            new_handler.setLevel(logging.DEBUG)
            new_handler.setFormatter(formatter)

            logger.addHandler(new_handler)
            logger.addHandler(unified_file_handler)


# Global LoggingManager instance
logging_manager = LoggingManager()


# Convenience functions to match the original API
def get_logger(name: str) -> logging.Logger:
    return logging_manager.get_logger(name)


def set_log_dir(new_dir: str) -> None:
    logging_manager.set_log_dir(new_dir)


def switch_log_to_file() -> None:
    logging_manager.switch_to_file()


def switch_log_to_stdout() -> None:
    logging_manager.switch_to_stdout()
