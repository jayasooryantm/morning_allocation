import pandas as pd

ALLOCATION_TEMPLATE_PATH = "files/Template/Allocation Template.xlsx"
ALLOCATION_DATABASE_PATH = "files/data/Monitor Data.xlsx"


def load_files(file_path: str, logger) -> pd.DataFrame:
    """
    Loads the files based on excel or csv from the file_path and returns a dataframe.
    """
    status_fileloading = "Success"
    try:
        if file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            logger.error(f"{file_path}:file type not supported")
            status_fileloading = "Failed"
    except Exception as e:
        logger.error(f"Error in occured: {file_path}: {e}")
        status_fileloading = "Failed"
    finally:
        logger.info(f"File loading complete: {status_fileloading}")


def get_column_names(logger) -> list:
    """
    Returns the column names from template and generate allocation dataset.
    """
    status_column_name = "Success"
    try:
        logger.info("Getting column names from template")
        allocation_template = load_files(
            file_path=ALLOCATION_TEMPLATE_PATH, logger=logger
        )
        return allocation_template.columns
    except Exception as e:
        status_column_name = "Failed"
        logger.error(f"Error in occured: {e}")
    finally:
        logger.info(f"Column names generated: {status_column_name}")


def transform_dataframe(dataframe: pd.DataFrame, columns: dict, logger) -> pd.DataFrame:
    """
    Change the heading of dataframe.
    """
    status_transform = "Success"
    try:
        logger.info("Changing column names of dataframe")
        dataframe.rename(columns=columns, inplace=True)

        logger.info("Dropping unwanted columns")
        dataframe.drop(
            columns=dataframe.columns.difference(columns.values()), inplace=True
        )

        return
    except Exception as e:
        status_transform = "Failed"
        logger.error(f"Error in occured: {e}")
    finally:
        logger.info(f"Column names of dataframe changed: {status_transform}")


def load_allocation_database(dataframe: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Load the excel database as dataframe.
    """
    status_load_database = "Success"
    try:
        logger.info("Loading data from excel.")
        return load_files(file_path=ALLOCATION_DATABASE_PATH, logger=logger)
    except Exception as e:
        status_load_database = "Failed"
        logger.error(f"Error in occured: {e}")
    finally:
        logger.info(f"Dataframe loaded to database: {status_load_database}")

    def allocation_process(
        monitor_db: pd.DataFrame, allocation_template: pd.DataFrame, logger
    ) -> pd.DataFrame:
        """
        Process the allocation of monitors.
        """
        status_allocation_process = "Success"
        try:
            logger.info("Starting monitoring allocation process")
            # allocation logic goes here
            return pd.DataFrame()
        except Exception as e:
            status_allocation_process = "Failed"
            logger.error(f"Error in occured: {e}")
        finally:
            logger.info(
                f"Monitoring allocation process complete: {status_allocation_process}"
            )
