import logging


class LoggerManager:
    def __init__(self):
        self.logger = logging.getLogger("LoggerManager")
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("./orgm/data/logs/log.txt")
        # file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
        )

        console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
        )

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, message, level="DEBUG"):
        level = getattr(logging, level.upper(), logging.DEBUG)
        self.logger.log(level, message)


if __name__ == "__main__":
    logger = LoggerManager()
    logger.log("Este es un mensaje de depuración.", "DEBUG")
    logger.log("Este es un mensaje de información.", "INFO")
    logger.log("Este es un mensaje de advertencia.", "WARNING")
    logger.log("Este es un mensaje de error.", "ERROR")
    logger.log("Este es un mensaje crítico.", "CRITICAL")
