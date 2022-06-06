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

import plotly.graph_objs as go
import numpy as np
from sqlalchemy import create_engine
import pymysql

excel_files_list = [".xls", ".xlsx", ".xlsm", ".xlsb", ".xltx",
                    ".xltm", ".xlt", ".xml", ".xlam", ".xla", ".xlw", ".xlr"]

fname = ""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                prevent_initial_callbacks=True, suppress_callback_exceptions=True, meta_tags = [{"name": "viewport", "content": "width=device-width"}], show_undo_redo=True)
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/test')
with engine.connect() as conn:
    result = conn.execution_options(stream_results=True).execute("ALTER DATABASE test CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
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
                    "left": "-550px",
                    "left": "15%",
                    'border': '1px'
                }),)

            ]),
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dcc.Link(html.Button("",n_clicks=0, className="visualizer",style={
                    # "padding":"3%",
                    'float': 'left',
                    "left": "-950px",
                    'border': '1px'
                }), href="/visualize")     
    ]),
    html.Div(id='output-data-upload'),
])

sqlEngine = create_engine('mysql+pymysql://root:@localhost:3306', pool_recycle=3600)
dbConnection = sqlEngine.connect()
frame = pd.read_sql("select * from test.solman", dbConnection)

#change to database
# reading dataframe
df = frame
df['Created On'] = pd.to_datetime(df['Created On'], format='%d.%m.%Y')
# specific features
irt_p = df['IRT Percentage %']
mpt_p = df['MPT Percentage %']
processor = df['Processor']
created = df['Created On']
confirmed=df['Confirmed']
cust_action = df['Customer Action']
withdrawn = df['Withdrawn']


page_2_layout = html.Div(
children = [
		# (First row) Header: Logo - Title - Last updated
		html.Div(
			children = [
				# Logo
				html.Div(
					children = [
						html.Img(
							src = app.get_asset_url("./logo.png"),
							id = "logo-image",
							style = {
								"height": "120px",
								"width": "auto",
								"margin-bottom": "15px"
							}
						),
						dcc.Link(html.Button("",n_clicks=0, className="back",style={
                    				# "padding":"3%",
                    				'border': '1px'
                					}), href="/")
					],
					className = "one-third column"
				),
				html.Div(
					children = [
						# Title and subtitle
						html.Div(
							children = [
								html.H3(
									children = "SolMan", #to change to dynamic
									style = {
										"margin-bottom": "0",
										"color": "white"
									}
								),
								html.H5(
									children = "Simple Static Visualizer",
									style = {
										"margin-bottom": "0",
										"color": "white"
									}
								)
							]
						)
					],
					className = "one-half column",
					id = 'title'
				)
			],
			id = "header",
			className = "row flex-display",
			style = {
				"margin-bottom": "25px"
			}
		),
		# (Third row): Value boxes - Donut chart - Line & Bars
		html.Div(
			children = [
				# (Column 2) Donut chart
				html.Div(
					children = [
						html.P(
							children = "Select Processor: ",
							className = "fix_label",
							style = {
								"color": "white"
							}
						),
						dcc.Dropdown(
							id = "w_countries",
							multi = False,
							searchable = True,
							value = "Elvin Yusifli",
							placeholder = "Select Processor",
							options = [{"label": c, "value": c} for c in (processor.unique())],
							className = "dcc_compon"
						),
						# Donut chart
						dcc.Graph(
							id = "pie_chart",
							config = {
								"displayModeBar": "hover"
							}
						)
					],
					className = "create_container four columns",
					style = {
						"maxWidth": "400px"
					}
				),
				# (Columns 3 & 4) bar and bars plot
				html.Div(
					children = [
						dcc.Graph(
							id = "bar_chart",
							config = {
								"displayModeBar": "hover"
							}
						)
					],
					className = "create_container five columns"
				),
				html.Div(
					children = [
						dcc.Graph(
							id = "line_chart",
							config = {
								"displayModeBar": "hover"
							}
						)
					],
					className = "create_container five columns"
				)
			],
			className = "row flex-display"
		),
	],
	id = "mainContainer",
	style = {
		"display": "flex",
		"flex-direction": "column"
	}
)
# Donut chart
@app.callback(
	Output(
		component_id = "pie_chart",
		component_property = "figure"
	),
	Input(
		component_id = "w_countries",
		component_property = "value"
	)
)
def update_pie_chart(w_countries):
	# List of colors
	colors = ["orange", "#dd1e35", "green"]
	conf = df[df["Processor"]==w_countries]["Confirmed"].count()
	cust = df[df["Processor"]==w_countries]["Customer Action"].count()
	withd = df[df["Processor"]==w_countries]["Withdrawn"].count()
	# Build the figure
	fig = {
		"data": [
			go.Pie(
				labels = ["Confirmed", "Customer Action", "Withdrawn"],
				values = [conf, cust, withd],
				marker = {
					"colors": colors
				},
				hoverinfo = "label+value+percent",
				textinfo = "label+value",
				hole = 0.7,
				rotation = 45,
				insidetextorientation = "radial"
			)
		],
		"layout": go.Layout(
			title = {
				"text": f"Total incidents {confirmed.count() + cust_action.count()+withdrawn.count()}",
				"y": 0.93,
				"x": 0.5,
				"xanchor": "center",
				"yanchor": "top"
			},
			titlefont = {
				"color": "white",
				"size": 20
			},
			font = {
				"family": "sans-serif",
				"color": "white",
				"size": 12
			},
			hovermode = "closest",
			paper_bgcolor = "#1f2c56",
			plot_bgcolor = "#1f2c56",
			legend = {
				"orientation": "h",
				"bgcolor": "#1f2c56",
				"xanchor": "center",
				"x": 0.5,
				"y": -0.7
			}
		)
	}
	# Return the figure
	return fig


# bar and bars chart
@app.callback(
	Output(
		component_id = "bar_chart",
		component_property = "figure"
	),
	Input(
		component_id = "w_countries",
		component_property = "value"
	)
)
def update_bar_chart(w_countries):
	# Build the figure
	fig = {
		"data": [
			go.Bar(
				x = processor,
				y = mpt_p,
				name = "Average MPT per Processor",
				marker = {
					"color": "orange"
				},
				hoverinfo = "text",
				hovertemplate = "<b>Date</b>: %{x} <br><b>Average MPT per Processor</b>: %{y:,.0f}<extra></extra>"
			),
		],
		"layout": go.Layout(
			title = {
				"text": f"Total MPT cases: {mpt_p.count()}",
				"y": 0.93,
				"x": 0.5,
				"xanchor": "center",
				"yanchor": "top"
			},
			titlefont = {
				"color": "white",
				"size": 20
			},
			xaxis = {
				"title": "<b>Processor</b>",
				"color": "white",
				"showline": True,
				"showgrid": True,
				"showticklabels": True,
				"linecolor": "white",
				"linewidth": 1,
				"ticks": "outside",
				"tickfont": {
					"family": "Aerial",
					"color": "white",
					"size": 12
				}
			},
			yaxis = {
				"title": "<b>Ave MPT</b>",
				"color": "white",
				"showline": True,
				"showgrid": True,
				"showticklabels": True,
				"linecolor": "white",
				"linewidth": 1,
				"ticks": "outside",
				"tickfont": {
					"family": "Aerial",
					"color": "white",
					"size": 12
				}
			},
			font = {
				"family": "sans-serif",
				"color": "white",
				"size": 12
			},
			hovermode = "closest",
			paper_bgcolor = "#1f2c56",
			plot_bgcolor = "#1f2c56",
			legend = {
				"orientation": "h",
				"bgcolor": "#1f2c56",
				"xanchor": "center",
				"x": 0.5,
				"y": -0.7
			}
		)
	}
	# Return the figure
	return fig

@app.callback(
	Output(
		component_id = "line_chart",
		component_property = "figure"
	),
	Input(
		component_id = "w_countries",
		component_property = "value"
	)
)
def update_line_chart(w_countries):
	# Build the figure
	dat = df[df['Processor']==w_countries]['Created On']
	incidents =  df[df['Processor']==w_countries]['IRT Percentage %']
	fig = {
		"data": [
			go.Scatter(
				x =   dat,   #[x.split('.')[2] for x in created],
				y = incidents,
				name = "Incident Count",
				mode = "lines+markers",
				line = {
					"width": 3,
					"color": "#ff00ff"
				},
				hoverinfo = "text",
				hovertemplate = "<b>Date</b>: %{x} <br><b>Number of incidents</b>: %{y:,.0f}<extra></extra>"
			)
		],
		"layout": go.Layout(
			title = {
				"text": f"Total incidents: {incidents.count()}",
				"y": 0.93,
				"x": 0.5,
				"xanchor": "center",
				"yanchor": "top"
			},
			titlefont = {
				"color": "white",
				"size": 20
			},
			xaxis = {
				"title": "<b>Processor</b>",
				"color": "white",
				"showline": True,
				"showgrid": True,
				"showticklabels": True,
				"linecolor": "white",
				"linewidth": 1,
				"ticks": "outside",
				"tickfont": {
					"family": "Aerial",
					"color": "white",
					"size": 12
				}
			},
			yaxis = {
				"title": "<b>Incidents</b>",
				"color": "white",
				"showline": True,
				"showgrid": True,
				"showticklabels": True,
				"linecolor": "white",
				"linewidth": 1,
				"ticks": "outside",
				"tickfont": {
					"family": "Aerial",
					"color": "white",
					"size": 12
				}
			},
			font = {
				"family": "sans-serif",
				"color": "white",
				"size": 12
			},
			hovermode = "closest",
			paper_bgcolor = "#1f2c56",
			plot_bgcolor = "#1f2c56",
			legend = {
				"orientation": "h",
				"bgcolor": "#1f2c56",
				"xanchor": "center",
				"x": 0.5,
				"y": -0.7
			}
		)
	}
	# Return the figure
	return fig

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
        dcc.Input(
            id='editing-columns-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='editing-columns-button', n_clicks=0),
        dash_table.DataTable(
            df.to_dict('records'),
			columns=  toNumeric(df),
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "rgb(204, 255, 62, 0.733)",
                    "border": "inherit !important",
                }
            ],
            id='table',
			sort_action='native',
			sort_mode="multi",
			filter_action='native',
			column_selectable="single",
            editable=True,
			row_deletable=True,
			page_action="native",
        	page_current= 0,
        	page_size= 20,
        ),
		
    	html.Button('Add Row', id='editing-rows-button', n_clicks=0),

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
            message='Danger danger! Are you sure you want to continue?',
        ),

        dcc.Download(id="submit"),

        html.Div(id='output-provider'),
        # dbc.Alert(
        #     "Uploaded",
        #     id="alert-auto",
        #     is_open=False,
        #     duration=2000,
        #     style={"position": "fixed", "top": 5, "right": 10, "width": "15%", "borderRadius":"5px"}
        # ),
    ])

@app.callback(
    Output('table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table', 'data'),
    State('table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('table', 'columns'),
    Input('editing-columns-button', 'n_clicks'),
    State('editing-columns-name', 'value'),
    State('table', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns

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
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index_page
    elif pathname == '/visualize':
        return page_2_layout

def toNumeric(df):
	columns = []
	for col in df.columns:
		col_options = {"name": col, "id": col}
		for value in df[col]:
			if not (isinstance(value, str)):
				col_options["type"] = "numeric"
		columns.append(col_options)
		print(columns)
	return columns

if __name__ == '__main__':
    app.run_server(debug=True)