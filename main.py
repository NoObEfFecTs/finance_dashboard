import sys
import os
import json
import logging
from datetime import *

from database import *
from dash import *
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
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

# setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s")

PACKAGE_PARENT = "../.."
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

external_scripts = [{'src': 'https://cdn.plot.ly/plotly-locale-de-latest.js'}]


app = dash.Dash(__name__, external_scripts=external_scripts,external_stylesheets=[dbc.themes.GRID, dbc.themes.BOOTSTRAP], assets_folder="./assets")

server = app.server
start_month = date.today().month
start_year = date.today().year
end_month = date.today().month
end_year = date.today().year

if start_month == 12:
    end_year += 1
    end_month = 1
else:
    end_month += 1




title = dbc.Row(
    dbc.Col(html.H2("Financial Information Daniel Fischer"),
    width=6)
)

primary_row = dbc.Row(
    [       
        dbc.Col(dbc.Button("Add Income", color="primary", id="income-btn", className="me-1"), md=2, xs=12),
        dbc.Col(dbc.Button("Add/Update Cost", color="primary", id="bank-btn", className="me-1"), md=2, xs=12),
        # dbc.Col(dcc.Dropdown(list(config["times"]), "this month", id='dd-times', disabled=False, clearable=False), md=3 ,xs=12),
        dbc.Col(dcc.DatePickerSingle(date=datetime(start_year, start_month, 1), id="start-date", display_format='D-M-Y'), md=2, xs=12),
        dbc.Col(dcc.DatePickerSingle(date=datetime(end_year, end_month, 1) + timedelta(days=-1),id="end-date", display_format='D-M-Y'), md=2, xs=12),
    ],
    align="center",
)

secondary_row = dbc.Row(
    [       
        # dbc.Col(dcc.Graph(id="graph1"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph1")], id="g1_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g1"),
        
        # dbc.Col(dcc.Graph(id="graph2"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph2")], id="g2_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g2"),
        
        # dbc.Col(dcc.Graph(id="graph3"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph3")], id="g3_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g3"),

        # dbc.Col(dcc.Graph(id="graph4"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph4")], id="g4_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g4"),

        # dbc.Col(dcc.Graph(id="graph5"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph5")], id="g5_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g5"),

        # dbc.Col(dcc.Graph(id="graph6"), md=12, lg=6, xxl=4),
        dbc.Col(html.Div([dcc.Graph(id="graph6")], id="g6_box"), md=12, lg=6, xxl=4),
        # dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}, id="spin_g6"),


        # dbc.Col(dbc.Progress(label="XX€", value=25, striped=True, color="success", animated=True), width=12),
    ],
    align="center",
)

storage = dcc.Store(
    id= "data-store",
    storage_type="memory",
    data = {
        "table" : {
            "category" : [None],
            "company" : [None],
            "user" : ["Daniel"],
            "target" : ["Daniel"],
            "date" : [f"{date.today():%Y-%m-%d}"],
            "amount" : [None]
        },
        "base_element" : {
            "category" : [None],
            "company" : [None],
            "user" : ["Daniel"],
            "target" : ["Daniel"],
            "date" : [f"{date.today():%Y-%m-%d}"],
            "amount" : [None]
        },
    }
)

income_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Add income"), close_button=True),
                dbc.ModalBody([
                   dbc.Row(
                        [
                            dbc.Col(
                                [
                                html.P("Choose Company:"),
                                dcc.Dropdown(config["employer"], None, id='dd-inc-company'),
                                # dcc.Input(id="dd-inc-company", type="text", autoComplete=True,  spellCheck=True),
                                html.P("Choose Date:"),
                                dcc.DatePickerSingle(
                                    date=date.today(),
                                    id="inc-date",
                                    display_format='D-M-Y',
                                ),
                                html.P("Choose Buyer:"),
                                dcc.Dropdown(list(config["user"]), "Daniel", id='dd-inc-user', disabled=True),
                                html.P("Choose Target:"),
                                dcc.Dropdown(list(config["targets"]), "Daniel", id='dd-inc-target', disabled=True),
                                html.P("Add Amount:"),
                                dcc.Input(
                                    id="inc-amount",
                                    type="number",
                                    placeholder="10,00",
                                ),
                                dcc.Loading(
                                    id="inc-ls-loading",
                                    children=[html.Div([html.Div(id="inc-ls-loading-output-2")])],
                                    type="circle",
                                )
                                ],
                                width=12,
                            )
                        ],
                        className="g-3",
                    ),
                ]),
                
                dbc.ModalFooter(
                    dbc.Button(
                        "Submit",
                        id="inc-Submit",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="inc-modal",
            centered=True,
            is_open=False,
        ),
    ]
)


items = [
    dbc.DropdownMenuItem("First"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Second"),
]

bank_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Read Data from bank account"), close_button=True),
                dbc.ModalBody([
                    dbc.ListGroup(
                        
                        [
                            dbc.ListGroupItem([dcc.Dropdown(list(config["categorys"]), None, id="category_0", style={"width" : "150px"}),]),
                            dbc.ListGroupItem([dbc.Input(placeholder="Company", id="company_0"),]),
                            dbc.ListGroupItem([dcc.Dropdown(list(config["user"]), "Daniel", disabled=True, id="user_0" ,style={"width" : "100px"}),]),
                            dbc.ListGroupItem([dcc.Dropdown(list(config["targets"]), "Daniel", disabled=True, id="target_0" ,style={"width" : "100px"}),]),
                            dbc.ListGroupItem([dcc.DatePickerSingle(date=date.today(), id="date_0", display_format='D-M-Y'),]),
                            dbc.ListGroupItem([dbc.Input(placeholder="10,30", id="amount_0")]),
                            dbc.ListGroupItem([dbc.Button("Remove", color="danger", className="me-1", id={'type': 'remove-btn', 'index': 'rm_0'} , disabled=True, n_clicks=0)]),
                        ],
                        horizontal=True,
                        id="list-group"   
                    ),
                ],
                id = "bank-body"
                ),                
                dbc.ModalFooter(dbc.Row([
                    dbc.Col(dbc.Button(
                        "Read data",
                        id="bank-read",
                        className="ms-2",
                        n_clicks=0
                    )),
                    dbc.Col(dbc.Button(
                        "New Row",
                        id="bank-add",
                        className="ms-2",
                        n_clicks=0
                    )),
                    dbc.Col(dbc.Button(
                        "Submit",
                        id="bank-submit",
                        className="ms-auto",
                        n_clicks=0
                    )),
                    dbc.Col(dbc.Button(
                        "Delete",
                        id="bank-delete",
                        className="ms-auto",
                        n_clicks=0
                    )),
                    dbc.Col(dbc.Button(
                        "Update",
                        id="bank-update",
                        className="ms-auto",
                        n_clicks=0
                    )),
                ])
                ),
            ],
            id="bank-modal",
            centered=True,
            is_open=False,
            fullscreen="xxl-down",
            size="xl"
        )
    ])

app.layout = dbc.Container( children=[
    dbc.Col(
        [
            title,
            primary_row,
            secondary_row,
            income_modal,
            bank_modal
        ],
        width=12,
    ),
    storage
]
)

@app.callback(
    Output("bank-body", "children"),
    Output("data-store", "data"),
    Input("bank-submit", "n_clicks"),
    Input("bank-update", "n_clicks"),
    Input("bank-delete", "n_clicks"),
    Input("bank-add", "n_clicks"),
    Input({"type" : "remove-btn", "index": ALL}, "n_clicks"),
    State("bank-body", "children"),
    State("data-store", "data")
)

def update_rows(submit, update, delete, add_clicks, state, child, data):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    df = pd.DataFrame(data["table"])

    match trigger:
        case "bank-add":
            new_row = pd.DataFrame(data["base_element"])
            new_row = new_row.set_index(pd.Index([df.shape[0]]))
            df = pd.concat([df, new_row])
        case trigger if "{" in trigger  and "rm" in json.loads(trigger)["index"]:
            trigger = json.loads(trigger)["index"]
            del_col = int(trigger.split("_")[1])
            df = df.drop([del_col])
        case "bank-delete":
            delete_data(data)
        case "bank-submit":
            add_data(data, "cost")
        case "bank-update":
            update_data(data)

    # build ui table from data
    tmp_element = child[0]
    tmp_child = []
    for idx, row in df.iterrows():
        for col_idx, column in enumerate(tmp_element["props"]["children"]):
            tmp_id = tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["id"]
            if type(tmp_id) == type({}) and tmp_id["type"] == "remove-btn":
                tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["id"] = {'type': 'remove-btn', 'index': "rm_" + str(idx)}
                if df.shape[0] == 1:
                    tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["disabled"] = True
                else:
                    tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["disabled"] = False
                continue
            else:
                tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["id"].split("_")[0] += str(idx)
            
            tmp_element["props"]["children"][col_idx]["props"]["children"][0]["props"]["value"] = df[tmp_id.split("_")[0]].values[idx]
        tmp_child.append(tmp_element)
        
    data["table"] = df.to_dict(orient="list")
    return [tmp_child, data]
        
@app.callback(
    Output("inc-ls-loading", "children"),
    Input("inc-Submit", "n_clicks"),
    State("dd-inc-user", "value"),
    State("inc-date", "date"),
    State("inc-amount", "value"),
)

def add_income(clicks, person, date, amount):   
    if amount != None:
        # return
        data = [{
            "person" : person,
            "date" : date,
            "amount" : amount
        }]
        add_data(data, "income")
    return


@app.callback(
    Output("bank-modal", "is_open"),
    Input("bank-btn", "n_clicks"),
    Input("bank-submit", "n_clicks"),
)

def open_bank_modal(bank_clicks, submit_clicks):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    match trigger:
        case "bank-btn":
            return True
        case "bank-Submit":
            return False
        case _:
            return False


@app.callback(
    Output("inc-modal", "is_open"),
    Input("income-btn", "n_clicks"),
    Input("inc-Submit", "n_clicks"),
)

def open_inc_modal(inc_clicks, submit_clicks):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    match trigger:
        case "income-btn":
            return True
        case "inc-Submit":
            return False
        case _:
            return False

@app.callback(
    Output("graph1", "figure"),
    Output("graph2", "figure"),
    Output("graph3", "figure"),
    Output("graph4", "figure"),
    Output("graph5", "figure"),
    Output("graph6", "figure"),
    Output("g1_box", "hidden"),
    Output("g2_box", "hidden"),
    Output("g3_box", "hidden"),
    Output("g4_box", "hidden"),
    Output("g5_box", "hidden"),
    Output("g6_box", "hidden"),
    Output("end-date", "date"),
    Input("start-date", "date"),
    Input("end-date", "date"),
    Input("inc-Submit", "n_clicks"),
    State("start-date", "date"),
    State("end-date", "date")

)
def generate_chart(start_date, end_date, inc_sub, start_dat, end_dat):
        tmp_start = date(int(start_dat.split('-')[0]), int(start_dat.split('-')[1]), int(start_dat.split('-')[2][:2]))
        tmp_end = date(int(end_dat.split('-')[0]), int(end_dat.split('-')[1]), int(end_dat.split('-')[2][:2]))

        if (tmp_end -tmp_start).days < 0:
            tmp_end = date(int(start_dat.split('-')[0]), (int(start_dat.split('-')[1])+1)%12, 1) + timedelta(days=-1)
            end_date = "-".join([str(tmp_end.year), str(tmp_end.month), str(tmp_end.day)])


        if tmp_start == None or tmp_end == None:
            start= datetime(date.today().year, date.today().month, 1)
            end = datetime(date.today().year, date.today().month + 1, 1) + timedelta(days=-1)
            time = f"range(start: {start.strftime('%Y')}-{start.strftime('%m')}-{start.strftime('%d')}T11:00:00Z, stop: {end.strftime('%Y')}-{end.strftime('%m')}-{end.strftime('%d')}T13:00:00Z)"
        else:
            
            time = f"range(start: {tmp_start.strftime('%Y')}-{tmp_start.strftime('%m')}-{tmp_start.strftime('%d')}T11:00:00Z, stop: {tmp_end.strftime('%Y')}-{tmp_end.strftime('%m')}-{tmp_end.strftime('%d')}T13:00:00Z)"

        costs, income = read_data(time)
        
        if "result" in income.keys():
            income.pop("result")
        if "table" in income.keys():
            income.pop("table")
        if "result" in costs.keys():
            costs.pop("result")
        if "table" in costs.keys():
            costs.pop("table")
        
        df = pd.DataFrame(costs)

        if df.empty:
            fig_all = px.pie()
            figs = [fig_all] * 6
            return figs + 6* [True] + [end_date]

        cats = ["Lebensmittel", "Finanzen", "Wohnung", "Versicherungen"]

        fig_all = px.pie(df, values='amount', names='category')
        fig_all["layout"]["title"] = f"Alles {df.sum().amount.round(2)}€"
        fig_all["layout"]["font"]["size"] = 14
        fig_all.update_traces(textposition='inside', textinfo='value')

        i=0
        sum = df[df["category"] == cats[i]].sum().amount.round(2)
        fig_groc = px.pie(df[df["category"] == cats[i]], values='amount', names='company')
        fig_groc["layout"]["title"] = f"{cats[i]} {sum}€"
        fig_groc["layout"]["font"]["size"] = 14
        fig_groc.update_traces(textposition='inside', textinfo='value')

        i=1
        sum=df[df["category"] == cats[i]].sum().amount.round(2)
        fig_fin = px.pie(df[df["category"] == cats[i]], values='amount', names='company')
        fig_fin["layout"]["title"] = f"{cats[i]} {sum}€"
        fig_fin["layout"]["font"]["size"] = 14
        fig_fin.update_traces(textposition='inside', textinfo='value')

        i=2
        sum = df[df["category"] == cats[i]].sum().amount.round(2)
        fig_elek = px.pie(df[df["category"] == cats[i]], values='amount', names='company')
        fig_elek["layout"]["title"] = f"{cats[i]} {sum}€"
        fig_elek["layout"]["font"]["size"] = 14
        fig_elek.update_traces(textposition='inside', textinfo='value')

        i=3
        sum=df[df["category"] == cats[i]].sum().amount.round(2)
        fig_vers = px.pie(df[df["category"] == cats[i]], values='amount', names='company')
        fig_vers["layout"]["title"] = f"{cats[i]} {sum}€"
        fig_vers["layout"]["font"]["size"] = 14
        fig_vers.update_traces(textposition='inside', textinfo='value')

        sum=df[df["category"].isin(cats) == False].sum().amount.round(2)
        fig_sonst = px.pie(df[df["category"].isin(cats) == False], values='amount', names='company')
        fig_sonst["layout"]["title"] = f"Sonstiges {sum}€"
        fig_sonst["layout"]["font"]["size"] = 14
        fig_sonst.update_traces(textposition='inside', textinfo='value')

        return [fig_all, fig_groc, fig_fin, fig_elek, fig_vers, fig_sonst] + 6* [False] + [end_date]


if __name__ == "__main__":
    # app.run_server(debug=False)
    app.run_server(host='192.168.188.20', port=8050, debug=True, use_debugger=True, use_reloader=True)