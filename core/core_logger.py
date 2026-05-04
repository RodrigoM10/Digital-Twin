import csv
import os 
from datetime import datetime

class DataLogger:
    def __init__(self, fillname="telemetry_log.csv"):
        self.filname = fillname
        self.file_exists = os.path.isfile(self.filname)
    
    def log_data(self, equipment_name, target, current_value, valve_pos):
        "Save a row of data in a CSV file"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # CSV Headers
        headers = ["Timestamp", "Equipment", "Target", "Current_Value", "Valve_Pos"]
    
        try:
            with open(self.filname, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)

                # if is a new file
                if not self.file_exists:
                    writer.writeheader()
                    self.file_exists = True
                
                writer.writerow({
                    "Timestamp": timestamp,
                    "Equipment": equipment_name,
                    "Target": target,
                    "Current_Value": round(current_value, 2),
                    "Valve_Pos": round(valve_pos, 2)
                })
        except Exception as e:
            print(f'Error writing to log: {e}')
