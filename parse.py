import pandas as pd
import os
import sys
import glob

def get_data():
    path = os.path.join(sys.path[0])
    file = glob.glob("*.ods", root_dir=path)
    file_path = os.path.join(path, file[0])
    data = pd.read_excel(file_path,sheet_name="Daten")

    return data

def parse_data():
    data = get_data()
    data = data[data.columns[:6]]
    data = data.query(f"Datum == Datum")
    values = {"Person" : "Helga"}
    data = data.fillna(value=values)
    data.to_csv("Data.csv", index=False)

if __name__ == "__main__":
    parse_data()