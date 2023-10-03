from abc import ABC, abstractmethod

import logging
import colorlog


class Logger(ABC):

    @abstractmethod
    def log(self, **kwargs):
        ''' log stuff '''


class TerminalLogger(Logger):

    def __init__(self):
        self._categories = {
            "INFO": "white"
        }
        self._logger = self._config_logger()

    def set_color(self, category: str, color: str):
        if category not in logging._nameToLevel:
            custom_level = max(logging._nameToLevel.values()) + 1
            logging.addLevelName(custom_level, category)
            self._categories[category] = color

    def log(self, text: str, category: str="INFO"):
        level = logging.getLevelName(category)
        self._logger.log(level, text)

    def _config_logger(self):
        logger = colorlog.getLogger()
        logger.setLevel(logging.INFO)

        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(message)s", log_colors=self._categories))

        logger.addHandler(handler)
        return logger
