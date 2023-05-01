import logging
import os
import json
import random
import pandas as pd
import numpy as np
from datetime import *
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# mode to check if demo is needed
mode = "prod"

if os.path.exists("/app/conf.json"):
    with open("/app/conf.json") as f:
        config = json.load(f)

else:
    if os.path.exists("conf.json"):
        with open("conf.json") as f:
            config = json.load(f)
    else:
        mode = "demo"
    
token = config["db_conf"]["token"]
org = config["db_conf"]["org"]
bucket = config["db_conf"]["bucket"]
url = config["db_conf"]["url"]

def delete_data(data):
    with InfluxDBClient(url=url, token=token, org=org) as client:
        for idx, row in data.iterrows():
            
            date = row["date"]
            person = row["user"]
            company = row["company"]
            category = row["category"]
            amount = row["amount"]
            mes = "cost"
            year = int(date.split("-")[0])
            month = int(date.split("-")[1])
            day = int(date.split("-")[2])
            start_tmp_date = datetime(year, month, day, 0, 0)
            end_tmp_date = datetime(year, month, day, 23, 0)
            delete_api = client.delete_api()
            delete_api.delete(start_tmp_date, end_tmp_date, f'_measurement={mes} AND category={category} AND company={company}', bucket=bucket, org=org)

    client.close()


def get_years():

    years = []

    with InfluxDBClient(url=url, token=token, org=org) as client:
        query = f'from(bucket: "finance") |> range(start: -100y)'
        result = client.query_api().query(org=org, query=query)
        if result != []:
            for table in result:
                for record in table.records:
                    tmp_year = record.get_time().year
                    if not tmp_year in years:
                        years.append(tmp_year)
    client.close()
    return years
def add_data(data, c_class):

    match c_class:
        case "inconme":
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
        case "cost":
            with InfluxDBClient(url=url, token=token, org=org) as client:
                for idx, row in data.iterrows():
                    date = row["date"]
                    person = row["user"]
                    company = row["company"]
                    category = row["category"]
                    if type(row["amount"]) == type(""):
                        amount = row["amount"].replace(",", ".")
                    else:
                        amount = row["amount"]
                    year = int(date.split("-")[0])
                    month = int(date.split("-")[1])
                    day = int(date.split("-")[2])
                    tmp_date = datetime(year, month, day, 12, 0)
                    point = Point("cost") \
                        .tag("category", category) \
                        .tag("company", company) \
                        .tag("user", person) \
                        .field("amount", float(amount)) \
                        .time(tmp_date, WritePrecision.NS)
                    write_api = client.write_api(write_options=SYNCHRONOUS)
                    write_api.write(bucket, org, point)
            client.close()

        case _:
            pass

def gen_test_data() -> pd.DataFrame:
    years = np.linspace(start=2010,stop=2030, num=21)
    categories = ["Lebensmittel", "Bus/Bahn", "Wohnung", "Bücher", "Versicherungen"]
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

    data_points = 4
    test_data = []

    for year in years:
        for ele in months:
            for i in range(0, data_points):
                test_ele = {"year": int(year) , "month" : ele, "category": random.choice(categories), "amount": random.randint(100, 1300)}
                test_data.append(test_ele)
    data = pd.DataFrame(test_data)
    data.sort_values("year")

    return data

def get_all_data():
    costs = {}
    income={}

    with InfluxDBClient(url=url, token=token, org=org) as client:
            query = 'from(bucket: "finance") |> range(start: -100y)'
            result = client.query_api().query(org=org, query=query)
            if result != []:
                for table in result:
                    for record in table.records:
                        match record.get_measurement():
                            case 'cost' :
                                if not record.get_field() in list(costs.keys()):
                                    costs[record.get_field()] = []
                                costs[record.get_field()].append(record.get_value())

                                tmp_date = record.values["_time"]
                                date = f"{tmp_date.year}-{tmp_date.month}-{tmp_date.day}"
                                mes = f"{record.values['_measurement']}"
                                if "date" not in list(costs.keys()):
                                    costs["date"] = []
                                costs["date"].append(date)
                                if "measurement" not in list(costs.keys()):
                                    costs["measurement"] = []
                                costs["measurement"].append(mes)
                                for ele in list(record.values.keys()):    
                                    if not "_" in ele:
                                        if not ele in list(costs.keys()):
                                            costs[ele] = []
                                        costs[ele].append(record.values.get(ele))
    client.close()
    tmp_data = pd.DataFrame(costs)
    tmp_data["date"] = pd.to_datetime(tmp_data.date)
    tmp_data["month"] = tmp_data.date.dt.month_name()
    tmp_data["year"] = tmp_data.date.dt.year

    return tmp_data

def get_monthly_data(year):
    
    core_cats = ["Wohnung", "Versicherungen", "Lebensmittel", "Finanzen"]

    res = {
        "category" : [],
        "month" : [],
        "year" : [],
        "amount" : []
    }

    if mode == "demo":
        data = gen_test_data()
        tmp_data = data.query(f"year == {year}")
        return tmp_data
    else:
        data = get_all_data()
    core_data = data.query(f"year == {year} and category in {core_cats}").groupby(["category", "month", "year"]).sum(numeric_only=True)

    for idx, row in core_data.iterrows():
        res["month"].append(idx[1])
        res["year"].append(idx[2])
        res["category"].append(idx[0])
        res["amount"].append(row.amount)

    rest_data = data.query(f"year == {year} and category not in {core_cats}").groupby(["year", "month"]).sum(numeric_only=True)
    for idx, row in rest_data.iterrows():
        res["month"].append(idx[1])
        res["year"].append(idx[0])
        res["category"].append("Sonstiges")
        res["amount"].append(row.amount)

    res = pd.DataFrame(res)
    return res

def get_year_data(years):

    if mode == "demo":
        years = [int(year) for year in years]
        data = gen_test_data()
    else:
        data = get_all_data()

    res = {
        "month" : [],
        "year" : [],
        "amount" : []
    }


    tmp_data = data.query(f"year in {years}").groupby(["month", "year"]).sum(numeric_only = True)

    for idx, row in tmp_data.iterrows():
        res["month"].append(idx[0])
        res["year"].append(idx[1])
        res["amount"].append(int(row.amount))
        
    return res

def read_data(timerange):
    costs = {}
    income = {}

    with InfluxDBClient(url=url, token=token, org=org) as client:
        query = f'from(bucket: "finance") |> {timerange}'
        result = client.query_api().query(org=org, query=query)
        if result != []:
            for table in result:
                for record in table.records:
                    match record.get_measurement():
                        case 'cost' :
                            if not record.get_field() in list(costs.keys()):
                                costs[record.get_field()] = []
                            costs[record.get_field()].append(record.get_value())

                            tmp_date = record.values["_time"]
                            date = f"{tmp_date.year}-{tmp_date.month}-{tmp_date.day}"
                            mes = f"{record.values['_measurement']}"
                            if "date" not in list(costs.keys()):
                                costs["date"] = []
                            costs["date"].append(date)
                            if "measurement" not in list(costs.keys()):
                                costs["measurement"] = []
                            costs["measurement"].append(mes)
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