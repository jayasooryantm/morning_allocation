import pandas as pd
from datetime import datetime as dt

monitor_db_path = "files/database/db_monitors.xlsx"
allocation_template_path = "files/database/db_allocation_template.xlsx"
subject_db_path = "files/database/db_subjects.xlsx"
powerbi_data_path = "files/input/data.xlsx"


def allocation_process(logger) -> None:
    """
    Process the allocation of monitors.
    """
    status_allocation_process = "Success"
    try:
        logger.info("Starting monitoring allocation process")
        # loading files
        logger.info("Loading files...")
        """power_bi_data = pd.read_excel(powerbi_data_path)
        monitor_db = pd.read_excel(monitor_db_path)
        allocation_data = pd.DataFrame()
        allocation_template = pd.read_excel(allocation_template_path)
        subject_db = pd.read_excel(subject_db_path)

        power_bi_data = power_bi_data[power_bi_data["Batch_Status"] != "Closed"]
        power_bi_data.reset_index(drop=True, inplace=True)
        allocation_data = power_bi_data[
            [
                "Subject Group",
                "Component",
                "Reviewer",
                "Batch ID",
                "Batch_Status",
                "Batch_Size",
            ]
        ]

        allocation_data = allocation_data.dropna(how="all").copy()
        for index, row in allocation_data[
            allocation_data["Subject Group"].isnull()
        ].iterrows():
            print(row["Subject Group"], row["Component"])

        allocation_data.insert(0, "Type", ["RM"] * len(allocation_data))
        allocation_data.to_csv("files/output/test_output.xlsx", index=False)"""

        monitor_data = pd.read_excel(monitor_db_path)
        data = pd.read_excel(powerbi_data_path)

        data.sort_values(by=["Subject Group", "Component"], inplace=True)

        for index, row in data.iterrows():
            row["Monitor"] = monitor_data[
                monitor_data["subject_group"] == row["Subject Group"]
                and (
                    row["Component"]
                    not in [
                        monitor_data["std_1"],
                        monitor_data["std_2"],
                        monitor_data["std_3"],
                        monitor_data["std_4"],
                        monitor_data["std_5"],
                        monitor_data["std_6"],
                        monitor_data["std_7"],
                        monitor_data["std_8"],
                        monitor_data["std_9"],
                    ]
                )
                and (
                    monitor_data[dt.today().strftime("%dd-%mmm")].to_string().lower()
                    == "yes"
                )
            ]
        return None
    except Exception as e:
        status_allocation_process = "Failed"
        logger.error(f"Error in occured: {e}")
    finally:
        logger.info(
            f"Monitoring allocation process complete: {status_allocation_process}"
        )
