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

        logger.info("Loading monitoring files...")
        monitor_data = pd.read_excel(monitor_db_path)
        data = pd.read_excel(powerbi_data_path)

        logger.info("Sorting data...")
        data.sort_values(by=["Subject Group", "Component"], inplace=True)

        grouped_data = data.groupby(by=['Subject Group', 'Component'], axis=0)
        date = dt.today().strftime("%d-%b")
        #-----------------------------------------------------------
        monitor_data[date] = monitor_data[date].astype('string')

        
        for key, value in grouped_data:
            # key[0], key[1] = 'Subject Group', 'Component'
            
            subject = key[0]
            
            print('-----------------------monitor data------------------------')
            temp = monitor_data[monitor_data[date] == 'Yes']
            available_monitors = temp[temp["subject_group"]==subject]

            if available_monitors:
                print(available_monitors)

            
                                
        return None
    except Exception as e:
        status_allocation_process = "Failed"
        logger.error(f"Error occured: {e}")
    finally:
        logger.info(
            f"Monitoring allocation process complete: {status_allocation_process}"
        )
