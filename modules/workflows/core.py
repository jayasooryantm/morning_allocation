import pandas as pd
from datetime import datetime as dt

monitor_db_path = "files/database/db_monitors.xlsx"
allocation_template_path = "files/database/db_allocation_template.xlsx"
subject_db_path = "files/database/db_subjects.xlsx"
powerbi_data_path = "files/input/data.xlsx"
output_data_path = "files/output/Allocation.xlsx"
shortname_data_path = "files/database/db_shortnames.xlsx"


def allocation_process(logger) -> None:
    """
    Process the allocation of monitors.
    """
    status_allocation_process = "Success"
    try:
        logger.info("Starting monitoring allocation process")
        # loading files
        logger.info("Loading files...")

        logger.info("Loading monitoring files...")
        monitor_data = pd.read_excel(monitor_db_path)
        data = pd.read_excel(powerbi_data_path)
        shortnames = pd.read_excel(shortname_data_path)

        logger.info("Removing closed monitoring data...")
        data = data[data["Status"] != "Closed"].copy()
        logger.info("Sorting data...")
        data.sort_values(by=["Subject Group", "Component"], inplace=True)

        date = dt.today().strftime("%d-%b")
        monitor_data[date] = monitor_data[date].astype("string")

        for index, row in data.iterrows():
            available_monitors = monitor_data[monitor_data[date] == "Yes"].copy(
                deep=False
            )

            names_array = shortnames[
                shortnames["short_name"].apply(
                    lambda x: str(x) == str(row["locked_by"])
                )
            ]

            if not names_array.empty:
                logger.info("Assigning locked monitor data...")
                name = names_array.iloc[0, 1]
                output = monitor_data[monitor_data[date] == "Yes"].copy(deep=False)
                output = output[output["monitor_name"] == name].copy(deep=False)

                if not output.empty:
                    data.loc[index, "Monitor"] = name
                    data.loc[index, "Comment"] = "Already locked batch"
                else:
                    data.loc[
                        index, "Comment"
                    ] = "Monitor previously made corrections - not in today, so reallocated"

        for index, row in data.iterrows():
            available_monitors = monitor_data[
                (monitor_data[date] == "Yes")
                & (monitor_data["subject_group"] == row["Subject Group"])
            ].copy(deep=False)

            if not available_monitors.empty:
                for i, monitor_row in available_monitors.iterrows():

                    name = str(monitor_row["monitor_name"])
                    standardised = str(monitor_row["standardised"]).split(",")
                    current_load = len(
                        data[data["Monitor"].apply(lambda x: str(x) == name)]
                    )

                    if (
                        (current_load < 11)
                        and (row["Component"] not in standardised)
                        and (str(row["Monitor"]).strip() == "nan")
                    ):
                        data.loc[index, "Monitor"] = name
                        logger.info("1 Monitor assigned...")

            # saving allocation data
        data.to_excel(output_data_path, index=False)
        logger.info("Allocation data saved successfully.")

        return None

    except Exception as e:
        status_allocation_process = "Failed"
        logger.error(f"Error occured: {e}")
    finally:
        logger.info(
            f"Monitoring allocation process complete: {status_allocation_process}"
        )
