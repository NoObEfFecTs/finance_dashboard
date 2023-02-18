import logging
import json
import pandas as pd
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
    