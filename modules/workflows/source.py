# Python libraries
from datetime import datetime as dt

# Custom modules
from modules.log_control import logging_functions
from modules.workflows.core import process_flow

# GLOBAL VARIABLES
LOG_LEVEL: int = 10  # DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40, CRITICAL = 50
LOG_FILE_PATH = f"files/logs/Log_{dt.today().date()}.log"


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

    logger.info("------------------------- Allocation Started ----------------------------------")

    # calls allocation function.

    status = process_flow(logger)
    if status:
        print("Allocation Process: Success")
        logger.info("------------------------- Allocation Finished Successfully --------------------")
    elif status:
        print("Allocation Process: Failed")
        logger.info("------------------------- Allocation Incomplete -------------------------")
    else:
        print(f"Unknown Status Returned: {status}")
    
    input("Press enter to finish...")
    
