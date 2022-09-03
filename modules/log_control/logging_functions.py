import logging


def get_console_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger with the given name and level.

        input:
            name: name module
            level: level of logging

        output:
            logger: logger with the given name and level
    """

    # create logger and set logging level
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create formatter, console handler and set logging level
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    console_handler = logging.StreamHandler()

    # add formatter to console handler
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # add console handler to logger
    logger.addHandler(console_handler)
    return logger


def get_file_logger(
    name: str,
    filename: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Get a logger with the given name and level.

        input:
            name: name module
            level: level of logging
            filename: name of the log file

        output:
            logger: logger with the given name and level
    """

    # create logger and set logging level
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create formatter, file handler and set logging level
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    file_handler = logging.FileHandler(filename)

    # add formatter to file handler
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)
    return logger
