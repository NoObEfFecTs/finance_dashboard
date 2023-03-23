import logging
import json
import random
import pandas as pd
import numpy as np
from datetime import *
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

local = True
if local:
    with open("conf.json") as f:
        config = json.load(f)
else:

    with open("/app/conf.json") as f:
        config = json.load(f)

token = config["db_conf"]["token"]
org = config["db_conf"]["org"]
bucket = config["db_conf"]["bucket"]
url = config["db_conf"]["url"]

def update_data(data, timerange):
    pass

def delete_data(data, timerange):
    pass

def add_data(data, type):

    if type == "income":

        with InfluxDBClient(url=url, token=token, org=org) as client:
            for row in data:
                date = row["date"]
                person = row["person"]
                amount = row["amount"]
                year = int(date.split("-")[0])
                month = int(date.split("-")[1])
                day = int(date.split("-")[2])
                tmp_date = datetime(year, month, day, 12, 0)
                point = Point("income") \
                    .tag("user", person) \
                    .field("amount", float(amount)) \
                    .time(tmp_date, WritePrecision.NS)
                write_api = client.write_api(write_options=SYNCHRONOUS)
                write_api.write(bucket, org, point)
        client.close()

    else:
        pass

def get_monthly_data():

    categories = ["Lebensmittel", "Bus/Bahn", "Wohnung", "Bücher", "Versicherungen"]
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

    data_points = 3

    test_data = []
    
    for ele in months:
        for i in range(0, data_points):
            test_ele = {"month" : ele, "category": random.choice(categories), "amount": random.randint(100, 1300)}
            test_data.append(test_ele)

    return pd.DataFrame(test_data)

def get_year_data():
    years = np.linspace(start=2010,stop=2030, num=21)
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    
    lines = 5

    tmp_years = []

    while len(tmp_years) < lines:
        year = random.choice(years)
        if not year in tmp_years:
            tmp_years.append(year)

    test_data = []
    for year in tmp_years:
        for ele in months:
            test_ele = {"year" : year, "month" : ele, "amount": random.randint(1000, 3000)}
            test_data.append(test_ele)
    

    return pd.DataFrame(test_data)

def read_data(timerange):
    with InfluxDBClient(url=url, token=token, org=org) as client:
        query = f'from(bucket: "finance") |> {timerange}'
        result = client.query_api().query(org=org, query=query)
        costs = {}
        income = {}

        if result != []:
            for table in result:
                for record in table.records:
                    match record.get_measurement():
                        case 'cost' :
                            if not record.get_field() in list(costs.keys()):
                                costs[record.get_field()] = []
                            costs[record.get_field()].append(record.get_value())
                            for ele in list(record.values.keys()):
                                if not "_" in ele:
                                    if not ele in list(costs.keys()):
                                        costs[ele] = []
                                    costs[ele].append(record.values.get(ele))

                        case 'income':
                            if not record.get_field() in list(income.keys()):
                                income[record.get_field()] = []
                            income[record.get_field()].append(record.get_value())
                            for ele in list(record.values.keys()):
                                if not "_" in ele:
                                    if not ele in list(income.keys()):
                                        income[ele] = []
                                    income[ele].append(record.values.get(ele))
    client.close()
    return costs, income
    