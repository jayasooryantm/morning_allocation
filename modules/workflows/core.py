# Python libraries
from datetime import datetime as dt
import os
from typing import final

# Third-party libraries
import pandas as pd

# Custom modules

# Global Variables
global pb_data
global shortnames
global subject_data
global monitor_data
global monitor_data_2
global logger
global template_

# Input Paths
monitor_db_path = r"files/database/db_monitors.xlsx"
allocation_template_path = r"files/database/Allocation Template.xlsx"
subject_db_path = r"files/database/db_subjects.xlsx"
shortname_db_path = r"files/database/db_shortnames.xlsx"
powerbi_data_path = r"files/input/data.xlsx"


# Output Paths
output_folder = f"files/output/{dt.today().strftime('%y_%m_%d')}/"
output_data_path = f"{output_folder}Allocation {dt.today().strftime('%d.%m')}.xlsx"
output_report_path = f"{output_folder}Allocation Report {dt.today().strftime('%d.%m')}.xlsx"
allocation_capacity_data_path = f"{output_folder}Allocation Capacity {dt.today().strftime('%d.%m')}.xlsx"

# Variables
max_load_allowed = 13
date = dt.today().strftime("%d-%b")
status_allocation_process:str = "Success"

# 1) preparing resources for allocation

def load_data(path: str, _sheetname: str=None) -> pd.DataFrame:
    logger.info(f"Loading data from: {path}")
    try:
        if path.endswith((".xlsx", ".xls")) and (_sheetname == None):
            df_data = pd.read_excel(path)
        elif path.endswith((".xlsx", ".xls")) and (_sheetname != None):
            df_data = pd.read_excel(path, sheet_name=_sheetname)
        elif path.endswith(".csv"):
            df_data = pd.read_csv(path)
        return df_data
    except Exception as e:
        logger.error(f"Error while loading data: {e}")

# Call this function first to start the module in the right way.
        
def data_assign(log_ob) -> bool:
    """
    load the input and database files and store it as global variable inside core module scope.
    """
    global pb_data, template_, shortnames, monitor_data, monitor_data_2, status_allocation_process, logger, subject_data
    logger = log_ob
    
    status: bool = True
    try:
        logger.info("Loading input/database files...")
        template_ = load_data(allocation_template_path)
        pb_data = load_data(powerbi_data_path)
        dif = pb_data.columns.difference(template_.columns).shape[0]
        if dif != 0:
            logger.error("Power BI (input) file columns name should be exactly like template...")
            status = False
            raise Exception("Power BI (input) data columns are different.")
        logger.info("Removing closed monitoring data...")
        pb_data = pb_data[pb_data["Batch Status"] != "Closed"].copy()
        subject_data = load_data(subject_db_path)
        shortnames = load_data(shortname_db_path)
        monitor_data = load_data(monitor_db_path)
        monitor_data_2 = load_data(monitor_db_path, _sheetname = "Sheet2")
        return status
    except Exception as e:
        status_allocation_process = "Failed"
        status = False
        logger.error(f"Error occured: {e}")
    finally:
        logger.info(f"Files loading complete: {status_allocation_process}")

def filter_sort() -> bool:
    global pb_data, logger
    status:bool = True
    try:
        logger.info("Sorting data...")
        pb_data.sort_values(by=["Subject Group", "Component"], inplace=True)
        return status
    except Exception as e:
        status = False
        logger.error(f"Error occured: {e}")
    finally:
        logger.info("Data Sorted.")


def is_standardised(std_component: str, name:str) -> bool:
    standardised_array =  monitor_data[monitor_data["monitor_name"] == name]
    standardised: list = list(str(standardised_array.iloc[0, 5]).split(", "))
    if str(std_component) in standardised:
        return True
    elif std_component not in standardised:
        return False

    
def save_files() -> bool:
    status: bool = True
    try:
        filter_sort()
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        pb_data.to_excel(output_data_path, sheet_name='allocation', index=False)
        capacity_data = monitor_data[(monitor_data["current_load"].apply(lambda x: int(x) < max_load_allowed)) & (monitor_data[date].apply(lambda x: x == "Yes"))].copy()
        capacity_data.drop_duplicates(subset=["monitor_name"], inplace=True)
        capacity_data.sort_values(by="current_load", inplace=True)
        capacity_data[["subject_group", "monitor_name", "current_load"]].to_excel(allocation_capacity_data_path, sheet_name='capacity', index=False)

        logger.info("Allocation data saved successfully.")
        return status
    except Exception as e:
        logger.error(f"Error occured: {e}")
        status = False
    finally:
        logger.info("Files saved.")

def fill_empty_subject() -> bool:
    status: bool = True
    global pb_data, subject_data, logger
    try:
        logger.info("checking and assigning missing subject groups...")
        blank_subjects_df = pd.DataFrame(pb_data[pb_data["Subject Group"].apply(lambda x: str(x) == "nan")])
        for blank_sub_index, blank_sub_row in blank_subjects_df.iterrows():
            subject_found = subject_data[subject_data["Component"] == blank_sub_row["Component"]]
            pb_data.loc[blank_sub_index, "Subject Group"] = subject_found.iloc[0, 0]
        return status
    except Exception as e:
        logger.error(f"Error occured: {e}")
        return status

# 2) starting the allocation functions
def locked_by_assign() -> bool:
    global pb_data, shortnames, monitor_data
    status:bool = True
    logger.info("assigning locked_by monitors")
    locked_scripts = pb_data[pb_data["Locked_By"].apply(lambda x: str(x) != "nan")].copy()
    try:
        for index, row in locked_scripts.iterrows():
            names_array = shortnames[
                shortnames["short_name"].apply(
                    lambda x: str(x) == str(row["Locked_By"])
                    )]

            if not names_array.empty:
                name = names_array.iloc[0, 1]
                output = monitor_data[
                    (monitor_data[date] == "Yes") 
                    & 
                    (monitor_data["monitor_name"] == name)
                    ].copy(deep=False)
                if not output.empty:
                    pb_data.loc[index, "Monitor"] = name
                    pb_data.loc[index, "Comment"] = f"Batch locked by {name}"
                else:
                    pb_data.loc[
                        index, "Comment"
                    ] = "Batch locked yesterday - monitor absent, reallocating"
            else:
                pb_data.loc[index, "Monitor"] = "  "
                pb_data.loc[index, "Comment"] = f"Name not found in automation database."
        return status
    except Exception as e:
        status = False
        logger.error(f"Error occured: {e}")
    
    

def primary_allocation() -> bool:
    global pb_data, monitor_data, logger
    status = True
    logger.info("Starting primary allocation...")
    # loading all the nessaccery data with data_assign() function
    try:
        
        fill_empty_subject()
        subject_list: list = [x for x in pb_data['Subject Group'].unique() if str(x) != "nan"]

        for _subject in subject_list:
            pb_data_filtered = pd.DataFrame(pb_data[(pb_data['Subject Group'].apply(lambda x: str(x) == _subject)) & (pb_data['Monitor'].apply(lambda x: str(x).strip() == "nan"))])

            for sub_index, sub_row in pb_data_filtered.iterrows():
                
                available_monitors = monitor_data[monitor_data["subject_group"].apply(lambda x: x == _subject) & monitor_data[date].apply(lambda x: x == "Yes")]
                
                if sub_row['Monitor'] != "nan":
                    
                    for mon_index, mon_row in available_monitors.iterrows():
                        current_load = mon_row['current_load']
                        monitor_name = mon_row['monitor_name']

                        if not (str(mon_row['standardised']) == "nan"):
                            is_std: bool = is_standardised(std_component=sub_row['Component'], name=mon_row['monitor_name'])
                            if (not is_std == True) and (current_load < max_load_allowed):
                                pb_data.loc[sub_index, 'Monitor'] = mon_row['monitor_name']
                                current_load +=  1
                                monitor_data.loc[monitor_data['monitor_name'].apply(lambda x: str(x) == monitor_name), 'current_load'] = current_load
        return status
    except Exception as e:
        status = False
        logger.error(f"Error occured: {e}")
    finally:
        logger.info("Primary allocation completed.")

def secondary_allocation() -> bool:
    status: bool = True
    global pb_data, monitor_data_2, monitor_data
    logger.info("Secondary allocation completed.")
    subject_list: list = [x for x in pb_data['Subject Group'].unique() if str(x) != "nan"]
    try:
        for _subject in subject_list:
            pb_data_filtered = pd.DataFrame(pb_data[
                (pb_data['Subject Group'].apply(lambda x: str(x) == _subject))
                 & 
                (pb_data['Monitor'].apply(lambda x: str(x) == 'nan'))
                ])
            available_monitors = [x for x in monitor_data_2[_subject] if str(x) != "nan"]
            
            for sub_index, sub_row in pb_data_filtered.iterrows():
                for monitor_name in available_monitors:
                    monitor_details = monitor_data[(monitor_data["monitor_name"].apply(lambda x: str(x) == monitor_name)) & (monitor_data[date].apply(lambda x: x == "Yes"))]
                    
                    if not monitor_details.empty:
                        current_load:int = monitor_details.iloc[0, 4]
                        if not (str(monitor_details.iloc[0, 5]) == "nan"):
                            is_std: bool = is_standardised(std_component=sub_row['Component'], name=monitor_name)
                            if (is_std == False) and (current_load <= 12):
                                pb_data.loc[sub_index, 'Monitor'] = monitor_name
                                current_load +=  1
                                monitor_data.loc[monitor_data['monitor_name'].apply(lambda x: str(x) == monitor_name), 'current_load'] = current_load
                        else:
                            if (current_load < max_load_allowed):
                                pb_data.loc[sub_index, 'Monitor'] = monitor_name
                                current_load +=  1
                                monitor_data.loc[monitor_data['monitor_name'].apply(lambda x: str(x) == monitor_name), 'current_load'] = current_load
        return status
    except Exception as e:
        status = False
        logger.error(f"Error occured: {e}")
    finally:
        logger.info("Secondary allocation completed.")


def process_flow(log_object) -> bool:
    log_object.info("Process Workflow starting...")
    step_end = True
    try:
        data_assign(log_object)
        locked_by_assign()
        primary_allocation()
        secondary_allocation()
        save_files()
        return step_end
    except Exception as e:
        step_end = False
        logger.error(f"Error occured: {e}")
    finally:
        logger.info("Process Workflow completed.")