import base64
import datetime
import io
from click import style

import json
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback_context
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import dcc, html, dash_table
from pathlib import Path
import pandas as pd
import time
import sqlalchemy

import plotly.graph_objs as go
import numpy as np
from sqlalchemy import create_engine
import pymysql
import functions

excel_files_list = [".xls", ".xlsx", ".xlsm", ".xlsb", ".xltx",
                    ".xltm", ".xlt", ".xml", ".xlam", ".xla", ".xlw", ".xlr"]

fname = ""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#, show_undo_redo=True
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                prevent_initial_callbacks=True, suppress_callback_exceptions=True, meta_tags = [{"name": "viewport", "content": "width=device-width"}])
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


sqlEngine = create_engine('mysql+pymysql://root:@localhost:3306/test', pool_recycle=3600)
dbConnection = sqlEngine.connect()
tables_list = pd.read_sql("show tables;", dbConnection)
df = pd.DataFrame()

#change to database
# reading dataframe



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
			html.Div([
    	html.H1('Select Table', style={"color":"white"}),
    	dcc.Dropdown(tables_list.Tables_in_test, '', id='page-1-dropdown'),
		html.Br(),
	
		]),
		html.Div(id="chart_buttons"),
    	html.Br(),
		
		# Viz part
    	html.Div(id="chart_container", children=[]),

		],
		id = "mainContainer",
		style = {
			"display": "flex",
			"flex-direction": "column"
		},
			# persistence=True
		)
		
@app.callback(Output('chart_buttons', 'children'),
              [Input('page-1-dropdown', 'value')])
def chart_buttons_return(value):
	if value is not None:
		global df
		df = pd.read_sql(f"select * from test.`{value}`", dbConnection)
		# df['Created On'] = pd.to_datetime(df['Created On'], format='%d.%m.%Y')
		return	[
					html.Button(id='pie_button', 
						children=[html.Img(src='./assets/pie-chart.png',
										style={"width":"40px","height":"40px"})],
						style={"width":"60px","height":"60px","padding":"10px", "margin-right":"15px"}, n_clicks=0,
						title='Pie Chart'),
					html.Button(id='bar_button',  
						children=[html.Img(src='./assets/bar-chart.png',
										style={"width":"40px","height":"40px"})],
						style={"width":"60px","height":"60px","padding":"10px", "margin-right":"15px"}, n_clicks=0,
							title='Bar Chart'),
					html.Button(id='line_button', 
						children=[html.Img(src='./assets/line-chart.png',
										style={"width":"40px","height":"40px"})],
						style={"width":"60px","height":"60px","padding":"10px", "margin-right":"15px"}, n_clicks=0,
						title='Line Chart'),
					html.Button(id='clear_button', 
						children=[html.Img(src='./assets/clear.png',
										style={"width":"40px","height":"40px"})],
						style={"width":"60px","height":"60px","padding":"9px", "margin-right":"15px"}, n_clicks=0,
						title='Clear All'),
					]

@app.callback(Output('chart_container', 'children'),
			  [Input('pie_button', 'n_clicks'),
			  Input('bar_button', 'n_clicks'),
			  Input('line_button', 'n_clicks'),
			  Input('clear_button', 'n_clicks'),
			  Input({"type": "dynamic-delete_pie", "index": ALL}, "n_clicks"),
			  Input({"type": "dynamic-delete_bar", "index": ALL}, "n_clicks"),
			  Input({"type": "dynamic-delete_line", "index": ALL}, "n_clicks"),],
			  [State("chart_container", "children")])
def charts_return(btn1, btn2, btn3, btn4, btn5, btn6, btn7, children): #to be changed : b1-4 useless

	input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
	# print(input_id)
	if "index" in input_id:
		delete_chart = json.loads(input_id)["index"]
		# print(delete_chart)
		children = [
			chart
			for chart in children
			if "'index': " + str(delete_chart) not in str(chart)
		]
	else:
		changed_id = [p['prop_id'] for p in callback_context.triggered][0]
		# specific features
		columns = list(df.columns)
		if 'pie_button' in changed_id and btn1>=1:
			children.append(html.Div(
						children = [
							html.Button(
							"+",
							id={"type": "dynamic-delete_pie", "index": 0},
							n_clicks=0,
							style={
								# "color":"white",
								"font-size": "40px",
								"font-weight": "300",
								"padding":'0',
								"border":"None",
								# "display": "inline-block",
								"transform": "rotate(45deg)",
								"position": "absolute",
								"top": "5px",
								"right": "5px"}),
							html.P(
								children = "Select Target Column: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "pie_chart_target",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.P(
								children = "Select Slice Columns: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "pie_chart_slice",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.Div(id="pie_chart_placeholder", children=[]),

						],
						className = "create_container three columns",
						style = {
							# "maxWidth": "400px"
							}))
		
		elif 'bar_button' in changed_id  and btn2>=1 : 
			children.append(html.Div(
						children = [
							html.Button(
							"+",
							id={"type": "dynamic-delete_bar", "index": 1},
							n_clicks=0,
							style={
								# "color":"white",
								"font-size": "40px",
								"font-weight": "300",
								"padding":'0',
								"border":"None",
								# "display": "inline-block",
								"transform": "rotate(45deg)",
								"position": "absolute",
								"top": "5px",
								"right": "5px"}),
							html.P(
								children = "Select X Column: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "bar_chart_x",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.P(
								children = "Select Y Columns: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "bar_chart_y",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.Div(id="bar_chart_placeholder", children=[]),
							],
						className = "create_container four columns"
					))
		elif 'line_button' in changed_id and btn3>=1:
			children.append(html.Div(
						children = [
							html.Button(
							"+",
							id={"type": "dynamic-delete_line", "index": 2},
							n_clicks=0,
							style={
								# "color":"white",
								"font-size": "40px",
								"font-weight": "300",
								"padding":'0',
								"border":"None",
								# "display": "inline-block",
								"transform": "rotate(45deg)",
								"position": "absolute",
								"top": "5px",
								"right": "5px"}),
							html.P(
								children = "Select X Column: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "line_chart_x",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.P(
								children = "Select Y Columns: ",
								className = "fix_label",
								style = {
									"color": "white"
								}
							),
							dcc.Dropdown(
								id = "line_chart_y",
								multi = False,
								searchable = True,
								value = None,
								placeholder = "...click or type to select...",
								options = 
								[{"label": c, "value": c} for c in columns]
								,
								className = "dcc_compon"
							),
							html.Div(id="line_chart_placeholder", children=[]),
						],
						className = "create_container five columns"
					))

		elif 'clear_button' in changed_id:
			children.clear()
		else:
			return []
	
	return children					
		# Donut chart
@app.callback(
	Output("pie_chart_placeholder", "children"),
	Input(
		component_id = "pie_chart_target",
		component_property = "value" #target - value1
	),
	Input(
		component_id = "pie_chart_slice",
		component_property = "value" #slices - value2
	)
)
def update_pie_chart(value1, value2):
	# print(value1, value2)
	colors = ["orange", "#dd1e35", "green","red", "cyan", "yellow", "magenta"]
	# Build the figure
	
	fig = {
		"data": [
			go.Pie(
				labels = df[value1],
				values = df[value2],
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
				"text": f"Total incidents {df['Confirmed'].count() + df['Customer Action'].count()+df['Withdrawn'].count()}",
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
	graph = dcc.Graph(
				id = "pie_chart",
				figure = fig)
	return graph


# bar and bars chart
@app.callback(
	Output("bar_chart_placeholder", "children"),
	Input(
		component_id = "bar_chart_x",
		component_property = "value"
	),
	Input(
		component_id = "bar_chart_y",
		component_property = "value"
	)
)
def update_bar_chart(value1, value2):
	# Build the figure
	df_dict = functions.bar_dict(df, value1, value2, mode="sum") #to be changed : add another dropdown for count/sum

	fig = {
		"data": [
			go.Bar(
				x = list(df_dict.keys()),
				y = list(df_dict.values()),
				name = "Placeholder", #to be changed
				marker = {
					"color": "orange"
				},
				# hoverinfo = "text",
				# hovertemplate = "<b>Date</b>: %{x} <br><b>Average MPT per Processor</b>: %{y:,.0f}<extra></extra>"
			),
		],
		"layout": go.Layout(
			title = {
				"text": f"test", #to be changed
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
	graph =  dcc.Graph(
				id = "bar_chart",
				figure=fig,
				config = {
					"displayModeBar": "hover"
				}
			)
	return graph

	@app.callback(
	Output("line_chart_placeholder", "children"),
	Input(
	component_id = "line_chart_x",
	component_property = "value"
	),
	Input(
		component_id = "line_chart_y",
		component_property = "value"
	))
	def update_line_chart(value1, value2):
		print(value1, value2)
		# df["Created On"] =  pd.to_datetime(df["Created On"], format='%d.%m.%Y')
		# Build the figure
		fig = {
			"data": [
				go.Scatter(
					x = df[value1],   #to be changed : add date option
					y = df[value2],
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
					"text": f"Total {value2}: {df[value2].sum()}", #to be changed : sum or count
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
		graph = dcc.Graph(
				id = "line_chart",
				figure=fig,
				config = {
					"displayModeBar": "hover"
					}
				)
		return graph

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
	for col in sorted(df.columns):
		col_options = {"name": col, "id": col}
		for value in df[col]:
			if not (isinstance(value, str)):
				col_options["type"] = "numeric"
		columns.append(col_options)
	return columns

if __name__ == '__main__':
    app.run_server(debug=True)