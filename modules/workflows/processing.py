import pandas as pd


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


def get_column_names(dataframe: pd.DataFrame) -> dict:
    """
    Returns the column names from template and generate allocation dataset.
    """

    return dict(zip(dataframe.columns, dataframe.columns))


def transform_dataframe(dataframe: pd.DataFrame, columns: dict, logger) -> pd.DataFrame:
    """
    1) Change the heading of dataframe.
    """
    try:
        logger.info("Changing column names of dataframe")
        dataframe.rename(columns=columns, inplace=True)

        logger.info("Dropping unwanted columns")
        dataframe.drop(
            columns=dataframe.columns.difference(columns.values()), inplace=True
        )

        return
    except Exception as e:
        logger.error(f"Error in occured: {e}")
    finally:
        logger.info(f"Column names of dataframe changed.")
