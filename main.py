import base64
import datetime
import io
from click import style

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback_context
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
charts_dictionary = {
	0:""
}
fname = ""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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
# frame = pd.read_sql("select * from test.solman", dbConnection)
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
    html.Div(id="test"),

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


@app.callback(Output('test', 'children'),
			  [Input('pie_button', 'n_clicks')],
			  [Input('bar_button', 'n_clicks')],
			  [Input('line_button', 'n_clicks')],
			  [Input('clear_button', 'n_clicks')])
def charts_return(btn1, btn2, btn3, btn4):
	global charts_dictionary
	changed_id = [p['prop_id'] for p in callback_context.triggered][0]
	# specific features
	columns = list(df.columns)
	charts_dict_index = len(charts_dictionary)
	if 'pie_button' in changed_id:
		charts_dictionary[charts_dict_index] = html.Div(
					children = [
						html.Button("+",id='close_button',
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
							"right": "5px"},
							value='1'),
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
							placeholder = "...click to select...",
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
							multi = True,
							searchable = True,
							value = None,
							placeholder = "...click to select...",
							options = 
							[{"label": c, "value": c} for c in columns]
							,
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
					className = "create_container three columns",
					style = {
						"maxWidth": "400px"})
	
	elif 'bar_button' in changed_id:
		charts_dictionary[charts_dict_index] = html.Div(
					children = [
						html.P(
							children = "Select Y Column: ",
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
							placeholder = "...click to select...",
							options = 
							[{"label": c, "value": c} for c in columns]
							,
							className = "dcc_compon"
						),
						html.P(
							children = "Select X Columns: ",
							className = "fix_label",
							style = {
								"color": "white"
							}
						),
						dcc.Dropdown(
							id = "bar_chart_x",
							multi = True,
							searchable = True,
							value = None,
							placeholder = "...click to select...",
							options = 
							[{"label": c, "value": c} for c in columns]
							,
							className = "dcc_compon"
						),

						dcc.Graph(
							id = "bar_chart",
							config = {
								"displayModeBar": "hover"
							}
						)
					],
					className = "create_container four columns"
				)
	elif 'line_button' in changed_id:
		charts_dictionary[charts_dict_index] = html.Div(
					children = [
						html.P(
							children = "Select Y Column: ",
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
							placeholder = "...click to select...",
							options = 
							[{"label": c, "value": c} for c in columns]
							,
							className = "dcc_compon"
						),
						html.P(
							children = "Select X Columns: ",
							className = "fix_label",
							style = {
								"color": "white"
							}
						),
						dcc.Dropdown(
							id = "line_chart_x",
							multi = True,
							searchable = True,
							value = None,
							placeholder = "...click to select...",
							options = 
							[{"label": c, "value": c} for c in columns]
							,
							className = "dcc_compon"
						),

						dcc.Graph(
							id = "line_chart",
							config = {
								"displayModeBar": "hover"
							}
						)
					],
					className = "create_container five columns"
				)

	elif 'clear_button' in changed_id:
		charts_dictionary = {0:""}
	else:
		return None
	
	return list(charts_dictionary.values())


# Donut chart
@app.callback(
	Output(
		component_id = "pie_chart",
		component_property = "figure"
	),
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
	print(value1, value2)
	colors = ["orange", "#dd1e35", "green"]
	# Build the figure
	fig = {
		"data": [
			go.Pie(
				labels = value2,
				values = np.unique(df[value1]),
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
	return fig


# bar and bars chart
@app.callback(
	Output(
		component_id = "bar_chart",
		component_property = "figure"
	),
	Input(
		component_id = "bar_chart_y",
		component_property = "value"
	),
	Input(
		component_id = "bar_chart_x",
		component_property = "value"
	)
)
def update_bar_chart(y, x):
	# Build the figure
	fig = {
		"data": [
			go.Bar(
				x = df[x],
				y = df[y],
				name = "Placeholder",
				marker = {
					"color": "orange"
				},
				# hoverinfo = "text",
				# hovertemplate = "<b>Date</b>: %{x} <br><b>Average MPT per Processor</b>: %{y:,.0f}<extra></extra>"
			),
		],
		"layout": go.Layout(
			title = {
				"text": f"Total MPT cases: {df['MPT Percentage %'].count()}",
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
		component_id = "charts",
		component_property = "value"
	)
)
def update_line_chart(charts):
	# Build the figure
	dat = df[df['Processor']==charts]['Created On']
	incidents =  df[df['Processor']==charts]['IRT Percentage %']
	fig = {
		"data": [
			go.Scatter(
				x =   dat,   #[x.split('.')[2] for x in df['Created On']],
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
        #html.H5(Path(filename).stem, className="test"),
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
            editable=True,
			# persistence=True
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
            message='Danger danger! Are you sure you want to continue?',
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
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index_page
    elif pathname == '/visualize':
        return page_2_layout

if __name__ == '__main__':
    app.run_server(debug=True)