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
    dbc.Col(html.H2("Financial Information"),
    width=12,
    style={"text-align": "center"}
    ),
)

primary_row = dbc.Row(
    [       
        dbc.Col(dbc.Button("Add Income", color="primary", id="income-btn", class_name="me-1"), xxl=2, md=3, sm=6, xs=12),
        dbc.Col(dbc.Button("Add/Update Cost", color="primary", id="bank-btn", class_name="me-1"), xxl=2, md=3, sm=6, xs=12),
        dbc.Col(dcc.DatePickerSingle(date=datetime(start_year, start_month, 1), id="start-date", display_format='D-M-Y'), xxl=2, md=3, sm=6, xs=12),
        dbc.Col(dcc.DatePickerSingle(date=datetime(end_year, end_month, 1) + timedelta(days=-1),id="end-date", display_format='D-M-Y'), xxl=2, md=3, sm=6, xs=12),
        dbc.Col(dbc.Button("Year Overview", color="primary", id="year-btn", class_name="me-1"), xxl=2, md=3, sm=6, xs=12),

    ],
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

graph_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Graphs"), close_button=True),
                dbc.ModalBody([
                    dcc.Dropdown(options={"2021" : "2021", "2022" : "2022"}, value="2022", multi=False, clearable=False, id='dd-year-bar-fig', disabled=False),
                    dbc.Row(html.Div([dcc.Graph(id="overview-months")], id="overview_month_box"),),
                    dcc.Dropdown(options={"2021" : "2021", "2022" : "2022"}, value=["2021"], multi=True, clearable=False, id='dd-year-line-fig', disabled=False),
                    dbc.Row(html.Div([dcc.Graph(id="overview-years")], id="overview_years_box"),),
                ]),
            
            ],
            id="overview-modal",
            centered=True,
            is_open=False,
            fullscreen="xxl-down",
            size="xl"
        ),
    ]
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
                        class_name="g-3",
                    ),
                ]),
                
                dbc.ModalFooter(
                    dbc.Button(
                        "Submit",
                        id="inc-Submit",
                        class_name="ms-auto",
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


base_element = dbc.Row([
        dbc.Col(dcc.Dropdown(list(config["categorys"]), clearable=False, value="Lebensmittel", id={'type': 'category', 'index': 'category_0'}, style={"width" : "150px"}), style={"min-width": "150px", "padding" : "2px"}),
        dbc.Col(dbc.Input(placeholder="Company", value=None, id={'type': 'company', 'index': 'company_0'}, style={"min-width": "100px", "padding" : "2px"})),
        dbc.Col(dcc.Dropdown(list(config["user"]), clearable=False, value="Helga", disabled=False, id={'type': 'user', 'index': 'user_0'} ,style={"min-width" : "100px", "padding" : "2px"})),
        dbc.Col(dcc.DatePickerSingle(date=date.today(), id={'type': 'date', 'index': 'date_0'}, display_format='D-M-Y', style={"min-width" : "150px", "padding" : "2px"})),
        dbc.Col(dbc.Input(placeholder="10,30", value=None, id={'type': 'amount', 'index': 'amount_0'}, style={"min-width" : "100px", "padding" : "2px"})),
        dbc.Col(dbc.Button("Remove-Row", color="danger", class_name="me-1", id={'type': 'remove-btn', 'index': 'remove-btn_0'} , disabled=True, n_clicks=0, style={"padding" : "2px"}))
    ],
    style = {"padding" : "5px",
            "border": "2px solid rgba(0, 0, 0, 0.3)",
            "border-radius": "5px",
            "margin" : "10px",
            "opacity": 1.0
    }
),

bank_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Read Data from bank account"), close_button=True),
                dbc.ModalBody([
    
                    *base_element
                ],
                id = "bank-body",
                ),                
                dbc.ModalFooter(dbc.Row([
                    dbc.Col(dbc.Button(
                        "Read data",
                        id="bank-read",
                        class_name="me-1",
                        n_clicks=0,
                        color="info"
                    )),
                    dbc.Col(dbc.Button(
                        "Add Row",
                        id="bank-add",
                        class_name="me-1",
                        n_clicks=0,
                        color="primary"
                    )),
                    dbc.Col(dbc.Button(
                        "Submit",
                        id="bank-submit",
                        class_name="me-1",
                        n_clicks=0,
                        color="success"
                    )),
                    dbc.Col(dbc.Button(
                        "Delete",
                        id="bank-delete",
                        class_name="me-1",
                        n_clicks=0,
                        color="danger"
                    )),
                    dbc.Col(dbc.Button(
                        "Update",
                        id="bank-update",
                        class_name="me-1",
                        n_clicks=0,
                        color="warning"
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
            bank_modal,
            graph_modal
        ],
        width=12,
    ),
]
)

def table2child(table, child):
    df = pd.DataFrame(table)
    tmp_child = []
    for idx, row in df.iterrows():
        if df.shape[0] > 1:
            disab = False
        else:
            disab = True

        ele = dbc.Row([
            dbc.Col(dcc.Dropdown(list(config["categorys"]), clearable=False, value=row.category, id={'type': 'category', 'index': f'category_{idx}'}, style={"width" : "150px"}), style={"min-width": "150px", "padding" : "2px"}),
            dbc.Col(dbc.Input(placeholder="Company", value=row.company, id={'type': 'company', 'index': f'company_{idx}'}, style={"min-width": "100px", "padding" : "2px"})),
            dbc.Col(dcc.Dropdown(list(config["user"]), value=row.user, disabled=True, id={'type': 'user', 'index': f'user_{idx}'}, clearable=False ,style={"min-width" : "100px", "padding" : "2px"})),
            dbc.Col(dcc.DatePickerSingle(date=row.date, id={'type': 'date', 'index': f'date_{idx}'}, display_format='D-M-Y', style={"min-width" : "150px", "padding" : "2px"})),
            dbc.Col(dbc.Input(placeholder="10,30", value=row.amount, id={'type': 'amount', 'index': f'amount_{idx}'}, style={"min-width" : "100px", "padding" : "2px"})),
            dbc.Col(dbc.Button("Remove-Row", color="danger", class_name="me-1", id={'type': 'remove-btn', 'index': f'remove-btn_{idx}'} , disabled=disab, n_clicks=0, style={"padding" : "2px"}))
            ],
            style = {"padding" : "10px",
                    "border": "2px solid rgba(0, 0, 0, 0.3)",
                    "border-radius": "5px",
                    "opacity": 1.0,
                    "margin" : "10px"
                    },
                    
        ),
        tmp_child.append(*ele)
        ele = None
    return tmp_child

def child2table(child):
    df = {}
    for row in child:
        for col in row["props"]["children"][:-1]:
            element = col["props"]["children"]["props"]
            tmp_key = element["id"]["type"]
            if not tmp_key in list(df.keys()):
                df[tmp_key] = []
            match tmp_key:
                case "date":
                    df[tmp_key].append(element["date"])
                case _:
                    if  not "value" in list(element.keys()):
                        df[tmp_key].append(element["placeholder"])
                    else:   
                        df[tmp_key].append(element["value"])

    return pd.DataFrame(df)

"""
Callback that creates table from datastore and stores all changes made to the table items by the user
"""
@app.callback(
    Output("bank-body", "children"),
    Input({"type" : "remove-btn", "index": ALL}, "n_clicks"),
    Input("bank-add", "n_clicks"),
    State("bank-body", "children"),
    # Input("bank-body", "children"),
    # Input({"type" : "category", "index": ALL}, "value"),
    # Input({"type" : "company", "index": ALL}, "value"),
    # Input({"type" : "user", "index": ALL}, "value"),
    # Input({"type" : "target", "index": ALL}, "value"),
    # Input({"type" : "date", "index": ALL}, "date"),
    # Input({"type" : "amount", "index": ALL}, "value"),
    
    
)

def update_rows(remove_btn, new_row_clicks, child):

    raw_trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    df = child2table(child)
    if "{" in raw_trigger:
        trigger = json.loads(raw_trigger)["index"]
        
        match trigger:
            case trigger if "remove" in trigger:
                del_col = int(trigger.split("_")[1])
                df = df.drop([del_col])
                df = df.set_index(pd.Index(list(range(0, df.shape[0]))))
    else:
        match raw_trigger:
            case "bank-add":
                new_row = df.head(1)
                new_row = new_row.set_index(pd.Index([df.shape[0]]))
                df = pd.concat([df, new_row])
    # build ui table from data 
    test_child = table2child(df, child)
    return test_child
        
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
        Output("overview-months", "figure"),
        Output("overview-years", "figure"),
        Input("overview-modal", "is_open"),
        Input("dd-year-bar-fig", "value"),
        Input("dd-year-line-fig", "value"),
        State("dd-year-bar-fig", "value"),
        State("dd-year-line-fig", "value")
)

def create_overview(is_open, bar_val_dd, line_val_dd, bar_val_stat, line_val_stat):

    bar_val = bar_val_stat
    line_val = line_val_stat


    data = get_monthly_data(bar_val)
    bar_fig = px.bar(data, x="month", y="amount", barmode="stack", color="category", labels={"amount": "Betrag [€]", "month" : "Monate"})
    bar_fig["layout"]["title"] = "Monthly Overview"
    bar_fig["layout"]["font"]["size"] = 14
    bar_fig.update_traces(width=0.5)
    bar_fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            # zeroline=False,
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        plot_bgcolor='white',
    )

    data = get_year_data(line_val)
    line_fig = px.line(data, x="month", y="amount", color="year", symbol="year", labels={"amount": "Betrag [€]", "months" : "Monate"})
    line_fig["layout"]["title"] = "Yearly Overview"
    line_fig["layout"]["font"]["size"] = 14
    line_fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            # zeroline=False,
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        # autosize=False,
        # margin=dict(
        #     autoexpand=False,
        #     l=100,
        #     r=20,
        #     t=110,
        # ),
        # showlegend=False,
        plot_bgcolor='white'
    )
    return [bar_fig, line_fig]
        
@app.callback(
    Output("overview-modal", "is_open"),
    Input("year-btn", "n_clicks"),
)

def open_overview_modal(open_clicks):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    match trigger:
        case "year-btn":
            return True
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

    # costs, income = read_data(time)
    costs = {}
    income = {}
    
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
    # app.run_server(host='localhost', port=8050, debug=True, use_debugger=True, use_reloader=True)
     app.run_server(debug=True)