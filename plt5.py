import base64
import datetime
import io
from click import style

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from pathlib import Path
import pandas as pd
import time
import sqlalchemy
excel_files_list = [".xls", ".xlsx", ".xlsm", ".xlsb", ".xltx",
                    ".xltm", ".xlt", ".xml", ".xlam", ".xla", ".xlw", ".xlr"]

fname = ""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                prevent_initial_callbacks=True, suppress_callback_exceptions=True)
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/test')
engine.connect()

app.layout = html.Div([

    html.Div([
        html.Img(src=app.get_asset_url('./logo.png'),
                 style={'height': '110px',
                        'width': '200',
                        'margin-bottom': '5px',
                        'float': 'left',
                        'border': '1px'}),
    ]),
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.A(
                    dbc.Button(
            "", id='submit-val', n_clicks=0, className="file-upload-wrapper", style={
                    # "padding":"3%",
                    'float': 'left',
                    "left": "15%",
                    'border': '1px'
                }),)

            ]),
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
    ])
])


def parse_contents(contents, filename, date):
    global fname
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    fname = Path(filename).stem.lower()
    try:
        if Path(filename).suffix == 'csv':
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif Path(filename).suffix in excel_files_list:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(Path(filename).stem, className="test"),
        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "rgb(204, 255, 62, 0.733)",
                    "border": "inherit !important",
                }
            ],
            id='table',
            editable=True
        ),
        html.A(
            dbc.Button("Save to Database", 
                            id="btn", 
                            className="wrapper1"), 
                            href='/', 
                            style={'float': 'left',
                                    "left": "15%",
                                    'border': '1px'}),
        
        dcc.ConfirmDialogProvider(
            children=dbc.Button("Update and Continue", 
                                  className="wrapper1", style={'float': 'left',
                                                                "left": "15%",
                                                                'border': '1px'}),
            id='danger-danger-provider',
            message='Danger danger! Are you sure you want to continue?'
        ),

        dcc.Download(id="submit"),

        html.Div(id='output-provider'),
        dbc.Alert(
            "Uploaded",
            id="alert-auto",
            is_open=False,
            duration=2000,
            style={"position": "fixed", "top": 5, "right": 10, "width": "15%", "borderRadius":"5px"}
        ),

    ])

@app.callback(
    Output("alert-auto", "is_open"),
    [Input("output-data-upload", "n_clicks")],
    [State("alert-auto", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open
    
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output("submit", "data"),
              [Input("btn", "n_clicks")],
              [State("table", "data")])
def submit_table(n_clicks, data):
    df = pd.DataFrame.from_records(data)
    return df.to_sql(f"{fname}", con=engine, if_exists='replace')


@app.callback(Output('output-provider', 'children'),
              Input('danger-danger-provider', 'submit_n_clicks'),
              State("table", "data"))
def update_output(submit_n_clicks, data):
    if not submit_n_clicks:
        return ''
    else: 
        df = pd.DataFrame.from_records(data)
        return df.to_sql(f"{fname}", con=engine, if_exists='replace')

if __name__ == '__main__':
    app.run_server()
