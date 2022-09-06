from datetime import datetime as dt

from modules.log_control import logging_functions
from modules.workflows.core import allocation_process

LOG_LEVEL: int = 10  # DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40, CRITICAL = 50
LOG_FILE_PATH = f"files/logs/Log_{dt.today().date()}.log"
FILE_PATH = "files/file.csv"


def main():
    """
    Main function: runs all other workflows
    """
    # get logger
    logger = logging_functions.get_file_logger(
        name=__name__,
        filename=LOG_FILE_PATH,
        level=LOG_LEVEL,
    )
    logger.info("Allocation Started.")

    # do the automation here...

    allocation_process(logger=logger)

    logger.info("Allocation Finished.")
