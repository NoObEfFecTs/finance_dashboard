import pandas as pd
import numpy as np
import os
import sys
import glob
import random

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
    # values = {"Person" : "Helga"}
    # data = data.fillna(value=values)
    data.loc[:,"Geschäft"] = None
    cats = data["Kategorie"].unique()
    print(f"cats = {cats}")
    crit = f"Kategorie == 'Lebensmittel'"
    lebensmittel = data.query(crit)

    high_price = lebensmittel.query("Betrag > 45")
    shops = ["Rewe", "Lidl", "Kaufland", "Edeka"]
    stores = [random.choice(shops) for x in range(high_price.shape[0])]
    high_price.loc[:,"Geschäft"] = stores

    data.to_csv("Data.csv", index=False)



if __name__ == "__main__":
    parse_data()