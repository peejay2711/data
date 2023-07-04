import pyodbc
import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import numpy as np
from datetime import date
from dash.exceptions import PreventUpdate
import dash_auth



#Read the data 
VALID_USERNAME_PASSWORD_PAIRS = {
    'Mobileum': 'M@obileum23'
}

#dt=pd.read_csv("C:\\Users\\Prashant.Jha\\Downloads\\cdrs.csv")

cnxn = pyodbc.connect("Driver={SQL Server};Server=10.10.100.104;UID=EntConsumer;PWD=hq-Efq8|xCx%)J;Database=StagingStorage;")
dt = pd.read_sql_query(

'''select
po.SubscriberID as OrginatingNumber,ro.FromCountry as OrginatingCountry,t.RequestorName,rt.tocc+rt.tondc as CCNDC,rt.tocc+rt.tondc+OriginatingPlatform2 as Uniqe,
t.dateid as DATE,CallPickedUp,ro.Status,EU_Refiling as EU,Classification as Terminology,TestDirection as Directiontest,DATEDIFF(second,ro.ConnectedTimeStamp,ro.disconnectedtimestamp) Duration,rt.ToCountry,
t.customerid AS CUSTOMERID,r.SITEVerdict,routenameformatted,count(*) tests,sum(r.TestValidity) as Totaltest, sum(taskvalidity) valids,OriginatingPlatform2,pt.Subscriberid as Virtual_Main_number,sb.MainNumber
FROM Stg.Test t WITH (NOLOCK)
	JOIN Stg.Result r WITH (NOLOCK) ON r.TestID=t.TestID AND r.DateID=t.DateID
	JOIN Stg.ResultOriginating ro WITH (NOLOCK) ON ro.ResultID=r.ResultID AND ro.DateID=r.DateID
	JOIN Stg.Party po WITH (NOLOCK) ON po.PartyID=ro.PartyID AND po.DateID=ro.DateID
	JOIN Stg.ResultTerminating rt WITH (NOLOCK) ON rt.ResultID=r.ResultID AND rt.DateID=r.DateID
	JOIN Stg.Party pt WITH (NOLOCK) ON pt.PartyID=rt.PartyID AND pt.DateID=rt.DateID
	JOIN Stg.Modem mo WITH (NOLOCK) ON mo.code=pt.ModemID
	JOIN Stg.Network N WITH (NOLOCK) ON pt.NetworkID=N.Code
    JOIN Stg.lu_NetworkStatus as l ON N.StatusLookup=l.LookupID
	JOIN Stg.Channel ch WITH (NOLOCK) ON ch.code=pt.ChannelID
	JOIN Stg.Server sv WITH (NOLOCK) ON sv.code=pt.ServerID
	LEFT OUTER JOIN Stg.ResultForwarding rf WITH (NOLOCK) ON rf.ResultID=r.ResultID AND rf.DateID=r.DateID
	LEFT OUTER JOIN Stg.Party pf WITH (NOLOCK) ON pf.PartyID=rf.PartyID AND pf.DateID=rf.DateID
	LEFT OUTER JOIN domainmodel.[Config].[Subscriber] sb WITH (NOLOCK) ON pt.Subscriberid = sb.code

where
r.ExecuteDateTime BETWEEN GETDATE()-10 AND GETDATE() and t.customerid not like '%_EV_%' and OriginatingPlatform2 not like 'Platform'
group by   t.dateid,CallPickedUp,t.customerid,r.SITEVerdict,routenameformatted,OriginatingPlatform2,ro.Status,EU_Refiling,Classification,TestDirection,sb.MainNumber,pt.Subscriberid,po.SubscriberID,ro.FromCountry,t.RequestorName,rt.tocc+rt.tondc,rt.ToCountry,DATEDIFF(second,ro.ConnectedTimeStamp,ro.disconnectedtimestamp),rt.tocc+rt.tondc+OriginatingPlatform2''', cnxn)


csv_data = pd.read_csv('C:\\Users\\Prashant.Jha\\Rates.csv')

# Convert the common column to a common data type
csv_data['Uniqe'] = csv_data['Uniqe'].astype(str)
dt['Uniqe'] = dt['Uniqe'].astype(str)

# Perform data mapping based on the common column
df = pd.merge(dt, csv_data, on='Uniqe', how='left')

df["Terminology"] = df["Terminology"].replace("", "N/A")
df = df.dropna(subset=["Terminology"])


df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d').dt.strftime('%Y-%m-%d')


options_1 = [{'label': i, 'value': i} for i in df["CUSTOMERID"].unique()]

# Define the options for the second dropdown menu (CallPickedUp)
options_2 = [{'label': n, 'value': n} for n in df["MainNumber"].unique()if pd.notnull(n)]

# Define the options for the third dropdown menu (Terminology)
options_3 = [{'label': t, 'value': t} for t in df["Virtual_Main_number"].unique()if pd.notnull(t)]






external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


callpickup_options=df["OriginatingPlatform2"].unique()

app=dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],update_title='Loading...')
server = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
image_path = 'assets/my-image.png'


app.layout=html.Div(id='my-div',children=[
    html.Img(src=image_path,style={'width': '5%','float': 'center'}),
    html.Div([
        html.Div(id='header-div', style={'textAlign': 'center'}, children=[
        html.H1("FPS ANALYTICS-DASHBOARD", id='header-h1')
    ])


    ]),
    
    html.Div(
        [
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['DATE'].min(),
                max_date_allowed=df['DATE'].max(),
                start_date=df['DATE'].min(),
                end_date=df['DATE'].max(),
                start_date_placeholder_text="Start Period",
                end_date_placeholder_text="End Period",
                calendar_orientation='vertical'
            ),
        ],
        style={'width': '50%', 'display': 'inline-block','float': 'center'}
    ),
    
    html.Div(
        [
            dcc.Dropdown(
                 id='template',
                 options=[
                    {'label': 'Dark', 'value': 'plotly_dark'},
                    {'label': 'White', 'value': 'plotly_white'},
                    {'label': 'Grey', 'value': 'ggplot2'},
                    {'label': 'Breeze', 'value': 'seaborn'},
                    {'label': 'light_White', 'value': 'simple_white'}
        ],
         value='simple_white'
    ),
        ],
        style={'width' : '25%',
                'display': 'inline-block','float': 'right' }
        ),
    
    html.Div(children=[dcc.Graph(id='bar-plot-with-value-labels',
                    style={'width': '100%','display': 'inline-block',"border":"2px Navy solid"})]
    ),
    
    html.Div(
        [
            dcc.Dropdown(
                id="OriginatingPlatform2",
                options=[{
                    'label': i,
                    'value': i
                } for i  in callpickup_options],
                placeholder='Please select Platform',
                clearable=True,
                value ='All OriginatingPlatform2'),
        ],
        style={'width' : '25%',
                'display': 'inline-block','float': 'left' }
        ),
    

    html.Div(
        [
            #First Chart
            html.Div(
                [
                    dcc.Graph(id='FOPS-Graph',clear_on_unhover=True),
                ],
                style={'width':'100%','display':'inline-block',"border":"2px Navy solid"}
            )
        ]
    ),
    html.Div(
        [
            #totaltest
            html.Div(
                [
                    dcc.Graph(id='Totaltest',clear_on_unhover=True),
                ],
                style={'width' : '100%','display': 'inline-block','float': 'left',"border":"2px Navy solid"}
            )
        ]
    ),

    html.Div(
        [
            dcc.Dropdown(
                id="customer-name",
                options=[{
                    'label': r,
                    'value': r
                } for r  in df["CUSTOMERID"].unique()],
                placeholder='Please select Customer',
                clearable=True,
                value ='All CUSTOMERID'),
                
        ],
        style={'width' : '100%',
                'display': 'inline-block' }),
    html.Div(
        [
            #Schduler Chart
            html.Div(
                [
                    dcc.Graph(id='schdulerchart',clear_on_unhover=True),
                ],
                style={'width': '100%', 'display': 'inline-block','float': 'left',"border":"2px Navy solid"}
            )
        ]
    ),

    
    html.Div(
        [
            dcc.Dropdown(
                id="CUSTOMERID",
                options=[{
                    'label': d,
                    'value': d
                } for d  in df["CUSTOMERID"].unique()],
                placeholder='Please select Customer',
                clearable=True,
                value ='All CUSTOMERID'),
                
        ],
        style={'width' : '100%',
                'display': 'inline-block' }),
    html.Div(
        [
            #Second Chart
            html.Div(
                [
                    dcc.Graph(id='FOPS-Funnel',clear_on_unhover=True),
                ],
                style={'width': '50%', 'display': 'inline-block','float': 'left',"border":"2px Navy solid"}
            )
        ]
    ),


        
        html.Div(
        [
            #Third  Chart
            html.Div(
                [
                    dcc.Graph(id='Classfication-Pie',clear_on_unhover=True),
                ],
                style={'width': '50%','display': 'inline-block','float': 'center',"border":"2px Navy solid"}
            )
        ]
    ),


    html.Div([

    # First dropdown menu (CUSTOMERID)
         dcc.Dropdown(id='dropdown-1', options=options_1,placeholder='Please select Customer Name',clearable=False,multi=False,
        value='AirtelIN',style={'width' : '50%',
                'display': 'inline-block','float': 'left' }),
    # Second dropdown menu (MainNumber)
         dcc.Dropdown(id='dropdown-2', options=options_2, placeholder='Please select Main Number',clearable=True,multi=False,
         value='All MainNumber',style={'width' : '50%',
                'display': 'inline-block','float': 'center' }),
    # Third dropdown menu (Virtual_Main_number)
         dcc.Dropdown(id='dropdown-3', options=options_3,placeholder='Please select Virtual/Main Number',clearable=False,multi=False,
          value='Virtual_Main_number',style={'width' : '50%',
                'display': 'inline-block'}),
        # Button for resetting the filters

    html.Div(children=[

    # Other layout elements...

         html.Button(id='reset-button', n_clicks=0, children='Reset filters')
]),
    # Bar chart
         html.Div(
                [
                    dcc.Graph(id='bar-chart',clear_on_unhover=True),
                ],
                style={'width': '100%','display': 'inline-block',"border":"2px Navy solid"})
         
]),
    html.Div(
        [ 
            
            dcc.Dropdown(
                id='customer-id',
                options=[{'label': c, 'value': c} for c in df['CUSTOMERID'].unique()],
                placeholder='Select a customer ID',
                clearable=True,value ='All CUSTOMERID'
    ),
                
        ],
        style={'width' : '20%',
                'display': 'inline-block' }),
    html.Div(
        [
            dcc.Dropdown(
                id="OriginatingPlatform",
                options=[{
                    'label': b,
                    'value': b
                } for b  in df["OriginatingPlatform2"].unique()],
                placeholder='Please select Platform',
                clearable=True,
                value ='All OriginatingPlatform2'),
                
        ],
        style={'width' : '20%',
                'display': 'inline-block' }),
    
    html.Div(
        [ 
            
            dcc.Dropdown(
                id="Terminology",
                options=[{
                    'label': f,
                    'value': f
                } for f  in df["Terminology"].unique() if pd.notnull(f)],
                placeholder='Please select Classification',
                clearable=True,
                value ='SB'),
                
        ],
        style={'width' : '20%',
                'display': 'inline-block' }),
    
        
    html.Div(
        [ 
            
            dcc.Dropdown(
                id="EU",
                options=[{
                    'label': y,
                    'value': y
                } for y  in df["EU"].unique() if pd.notnull(y)],
                placeholder='Please select EU',
                clearable=True,
                value ='All EU'),
                
        ],
        style={'width' : '20%',
                'display': 'inline-block' }),
    
    html.Div(
        [
            dcc.Dropdown(
                id="CallPickedUp",
                options=[{
                    'label': n,
                    'value': n
                } for n  in df["CallPickedUp"].unique() if pd.notnull(n)],
                placeholder='Please select CallPickedUp',
                clearable=True,
                value ='All CallPickedUp'),
            
        ],
        style={'width' : '20%',
                'display': 'inline-block','float': 'right' }
    ),
    
    html.Div(
        [
            #last chart
            html.Div(
                [
                    dcc.Graph(id='bar-route',clear_on_unhover=True),
                ],
                style={'width':'100%','display':'inline-block'}
            )
        ]
    ),
    html.Div(children=[dcc.Graph(id='bar-plot',
                    style={'width': '100%','display': 'inline-block',"border":"2px Navy solid"})]
),
    html.Div(
        [
            dcc.Dropdown(
                id="OrginatingCountry",
                options=[{
                    'label': p,
                    'value': p
                } for p  in df["OrginatingCountry"].unique()],
                placeholder='Please select OrginatingCountry',
                clearable=True,
                value ='Cyprus'),
            
                
        ],
        style={'width' : '100%',
                'display': 'inline-block' }),

    
    html.Div(
        [
            #Second Chart
            html.Div(
                [
                    dcc.Graph(id='FOPSOrginatingCountry',clear_on_unhover=True),
                ],
                style={'width' : '100%','display': 'inline-block','float': 'left',"border":"2px Navy solid"}
            )
        ]
    ),

    # html.Div(
    #     [
    #         dcc.Dropdown(
    #             id="CUSTOMER",
    #             options=[{
    #                 'label': x,
    #                 'value': x
    #             } for x  in df["CUSTOMERID"].unique()if pd.notnull(x)],
    #             placeholder='Please select Customer',
    #             clearable=True,
    #             value ='All CUSTOMER'),
            
                
    #     ],
    #     style={'width' : '20%',
    #             'display': 'inline-block'}),
    
    html.Div(
        [
            dcc.Dropdown(
            id="CallPick",
            options=[{
                'label': o,
                'value': o
    } for o in df["CallPickedUp"].unique() if pd.notnull(o)],
    placeholder='Please select CallPickedUp',
    clearable=True,
    value='All CallPick'
),

            
        ],
        style={'width' : '20%',
                'display': 'inline-block'}
    ),

    html.Div(
        [
            dcc.Dropdown(
                id="Platform",
                options=[{
                    'label': k,
                    'value': k
                } for k  in df["OriginatingPlatform2"].unique()if pd.notnull(k)],
                placeholder='Please select Platform',
                clearable=True,
                value ='All Platform'),
                
        ],
        style={'width' : '20%',
                'display': 'inline-block' }),




   html.Div(
        [
            
            html.Div(
                [
                    dcc.Graph(id='fopsduration',clear_on_unhover=True),
                ],
                style={'width' : '100%','display': 'inline-block','float': 'left',"border":"2px Navy solid"}
            )
        ]
    ),
 
    
])
@app.callback(
    dash.dependencies.Output('header-h1','style'),
    [dash.dependencies.Input('template','value')])
def update_background(template):
    if template == "plotly_dark":
        return {'color':'white'}
    elif template == "plotly_white":
        return {'color':'black'}
    elif template == "ggplot2":
        return {'color':'black'}
    elif template == "seaborn":
        return {'color':'black'}
    elif template == "simple_white":
        return {'color':'black'}
    else:
        return {'color':'black'}


@app.callback(
    dash.dependencies.Output('my-div','style'),
    [dash.dependencies.Input('template','value')])
def update_background(template):
    if template == "plotly_dark":
        return {'backgroundColor':'black'}
    elif template == "plotly_white":
        return {'backgroundColor':'white'}
    elif template == "ggplot2":
        return {'backgroundColor':'#F0F0F0'}
    elif template == "seaborn":
        return {'backgroundColor':'#F0F0F0'}
    elif template == "simple_white":
        return {'backgroundColor':'white'}
    else:
        return {'backgroundColor':'white'}

@app.callback(
    dash.dependencies.Output('FOPS-Graph','figure'),
    [dash.dependencies.Input('OriginatingPlatform2','value'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])
def update_graph(OriginatingPlatform2, start_date, end_date,template):
    # Filter the data based on the selected options and dates
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    if OriginatingPlatform2 is None or OriginatingPlatform2 == []:
        OriginatingPlatform2 = 'All OriginatingPlatform2'
    if OriginatingPlatform2 != 'All OriginatingPlatform2':
        df_filtered = df_filtered[df_filtered['OriginatingPlatform2'] == OriginatingPlatform2]    
    # Update the graph using the filtered data
    pv = pd.pivot_table(df_filtered, index=['CUSTOMERID'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    try:
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='FOPS-Graph')
    try:
        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='FOPS-Graph')
    try:
        trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='FOPS-Graph')


    return{
        'data':[trace1,trace2,trace3],
        'layout':
        go.Layout(
            title='Platform-Wise Traffic status {}'.format(OriginatingPlatform2),
            barmode='stack',template=template,
            xaxis_title='Customer Name',
            yaxis_title='Test')
    }

@app.callback(
    dash.dependencies.Output('FOPS-Funnel','figure'),
    [dash.dependencies.Input('CUSTOMERID','value'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])
def update_graph(CUSTOMERID,start_date, end_date,template):
    df_plot = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    if CUSTOMERID is None or CUSTOMERID == []:
        CUSTOMERID = 'All CUSTOMERID'
    if CUSTOMERID != "All CUSTOMERID":
        df_plot = df_plot[df_plot['CUSTOMERID'] == CUSTOMERID]
    pv = pd.pivot_table(df_plot, index=['OriginatingPlatform2'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    
    try:
    
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='FOPS-Funnel')
    try:

        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='FOPS-Funnel')
    try:

       trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='FOPS-Funnel')
    
    

    return{
        'data':[trace1,trace2,trace3],

        'layout':
        go.Layout(
            title='Customer-Wise Traffic status {}'.format(CUSTOMERID),
            barmode='stack',template=template,
            xaxis_title='Platform Name',
            yaxis_title='Test')
}

@app.callback(
    dash.dependencies.Output("Classfication-Pie", "figure"),
    [dash.dependencies.Input("CUSTOMERID", "value"),
    dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')]
)

def update_pie(CUSTOMERID,start_date, end_date,template):
    df_plot = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    if CUSTOMERID is None or CUSTOMERID == []:
        CUSTOMERID = 'All CUSTOMERID'
    if CUSTOMERID != 'All CUSTOMERID':
        df_plot = df_plot[df_plot['CUSTOMERID'] == CUSTOMERID]
    #create a pie chart
    df2=df_plot.dropna(subset=["Terminology"])

    try:
       fig = px.pie(df2, values='tests', names='Terminology')
    except KeyError as e:
        print(f"Error: {e}")


    fig.update_layout(
        template=template,
        
    )
    return fig


#Filter for  Drop-Down List
@app.callback(
    [dash.dependencies.Output('dropdown-2', 'options'), dash.dependencies.Output('dropdown-3', 'options')],
    [dash.dependencies.Input('dropdown-1', 'value'),dash.dependencies.Input('dropdown-2', 'value')])
def update_dropdown_options(value_1,value_2):
    # Filter the data based on the selection in the first dropdown menu
    filtered_df = df[(df["CUSTOMERID"] == value_1) | (value_1 == 'All CUSTOMERID')]
    filtered_df = filtered_df[(filtered_df["MainNumber"] == value_2) | (value_2 == 'All MainNumber')]

    # Update the options for the second dropdown menu (SITEVerdict)
    options_2 = [{'label': v, 'value': v} for v in filtered_df["MainNumber"].unique()if pd.notnull(v)]
    # Update the options for the third dropdown menu (houroftest)
    options_3 = [{'label': h, 'value': h} for h in filtered_df["Virtual_Main_number"].unique()if pd.notnull(h)]
    return options_2, options_3
   
@app.callback(
    [
        dash.dependencies.Output('dropdown-2', 'value'),
        dash.dependencies.Output('dropdown-3', 'value')
    ],
    [dash.dependencies.Input('reset-button', 'n_clicks')]
)
def reset_dropdown_values(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        # Reset the dropdown values to their default values
        return 'All MainNumber', 'Virtual_Main_number'
    raise PreventUpdate

#Update Bar chart
@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('dropdown-1', 'value'), 
    dash.dependencies.Input('dropdown-2', 'value'), 
    dash.dependencies.Input('dropdown-3', 'value'),
    dash.dependencies.Input('reset-button', 'n_clicks'),
    dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])

def update_bar_chart(value_1, value_2, value_3,n_clicks,start_date, end_date,template):
    df2 = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    

    if n_clicks is not None and n_clicks > 0:
        reset_dropdown_values(n_clicks)

    filtered_df = df2[(df2["CUSTOMERID"] == value_1) | (value_1 == 'All CUSTOMERID')]
    filtered_df = filtered_df[(filtered_df["MainNumber"] == value_2) | (value_2 == 'All MainNumber')]
    filtered_df = filtered_df[(filtered_df["Virtual_Main_number"] == value_3) | (value_3 == 'Virtual_Main_number')]

    if filtered_df.empty:
        # Return an empty figure with the title 'bar-chart'
        return go.Figure(data=[], layout=go.Layout(title='Main-Traffic status',
            barmode='stack',template=template,
            xaxis_title='Main Number',
            yaxis_title='Test')),

    # Check if the 'MainNumber' column is blank
    if filtered_df['MainNumber'].isnull().all():
        # If it is, create the pivot table using the 'Virtual_Main_number' column as the index
         pv = pd.pivot_table(filtered_df, index=['Virtual_Main_number'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
         
    else:
        # Otherwise, create the pivot table using the 'MainNumber' column as the index
         pv = pd.pivot_table(filtered_df, index=['Virtual_Main_number'],columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    

    try:
    
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='bar-chart')
    try:

        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='bar-chart')
    try:

       trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='bar-chart')

    return{
        'data':[trace1,trace2,trace3],
        'layout':
        go.Layout(
            title='Customer-Wise Main-Virtual Traffic status',
            barmode='stack',template=template,
            xaxis_title='Virtual Number',
            yaxis_title='Total Test')

    }

@app.callback(
    dash.dependencies.Output('bar-plot-with-value-labels', 'figure'),
    [dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])
def update_graph(start_date, end_date,template):
    # Filter the data based on the selected date range
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    # Create a pivot table using the filtered data
    pv = pd.pivot_table(df_filtered, index=['CUSTOMERID'], values=['valids','tests'],aggfunc=sum,fill_value=0)
    total_rows = pv.shape[0]
    pv['Valid_percentage'] = round(pv['valids'] / pv['tests'] * 100).astype(str) + '%'
    pv = pv.sort_values('Valid_percentage', ascending=True)

    # Keep the CUSTOMERID column in the data frame
    pv = pv.reset_index(drop=False)

    # Generate a list of labels from the Valid_percentage column
    labels = pv['Valid_percentage']

    # Create a bar plot using the CUSTOMERID and Valid_percentage columns
    bar_plot = go.Bar(
        x=pv['CUSTOMERID'],
        y=pv['Valid_percentage'],
        name='Valid Percentage',
        text=labels,
        textposition='auto'
    )

    # Create a figure containing the bar plot
    layout = go.Layout(template=template,xaxis_title='Customer Name ',yaxis_title='Vald Percentage(%)')
    fig = go.Figure(data=[bar_plot],layout=layout)
    fig.update_yaxes( tickformat=".0%")

    return fig


@app.callback(
    dash.dependencies.Output('bar-plot', 'figure'),
    [dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])
def update_graph(start_date, end_date,template):

    try:
    # Filter the data based on the selected date range
         df_filtered = df.query("DATE >= @start_date and DATE <= @end_date and valids == 0 and tests > 25 ")
    
    except:

        df_filtered = df.query("DATE >= @start_date and DATE <= @end_date and valids == 0 and tests > 5 ")

    
    
    # Create a pivot table using the filtered data
    pv = pd.pivot_table(df_filtered, index=['routenameformatted'], values=['valids','tests'],aggfunc=sum,fill_value=0)
    

    # Keep the CUSTOMERID column in the data frame
    pv = pv.reset_index(drop=False)


    # Create a bar plot using the CUSTOMERID and Valid_percentage columns
    bar_plot = go.Bar(
        x=pv['routenameformatted'],
        y=pv['tests'],
        name='Valid Percentage',
        textposition='auto',
        marker=dict(color='orange')
    )

    # Create a figure containing the bar plot
    layout = go.Layout(template=template,xaxis_title='Routes Name ',yaxis_title='Total Failed Test')
    fig = go.Figure(data=[bar_plot],layout=layout)

    return fig

@app.callback(
    dash.dependencies.Output('bar-route','figure'),
    [dash.dependencies.Input('Terminology','value'),
    dash.dependencies.Input('OriginatingPlatform','value'),
     dash.dependencies.Input('customer-id', 'value'),
     dash.dependencies.Input('CallPickedUp','value'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('EU','value'),
     dash.dependencies.Input('template', 'value')])
def update_graph(Terminology,OriginatingPlatform2,customer_id, CallPickedUp, start_date, end_date,EU,template):
    # Filter the data based on the selected options and dates
    
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    if customer_id is None or customer_id == []:
        customer_id = 'All CUSTOMERID'
    if Terminology is None or Terminology == []:
        Terminology = 'All Terminology'
    if CallPickedUp is None or CallPickedUp == []:
        CallPickedUp = 'All CallPickedUp'
    if EU is None or EU == []:
       EU = 'All EU'
    if OriginatingPlatform2 is None or OriginatingPlatform2 == []:
       OriginatingPlatform2 = 'All OriginatingPlatform2'
    if Terminology != 'All Terminology':
        df_filtered = df_filtered[df_filtered['Terminology'] == Terminology]
    if CallPickedUp != 'All CallPickedUp':
        df_filtered = df_filtered[df_filtered['CallPickedUp'] == CallPickedUp]
    if customer_id != 'All CUSTOMERID':
        df_filtered = df_filtered[df_filtered['CUSTOMERID'] == customer_id]
    if EU != 'All EU':
        df_filtered = df_filtered[df_filtered['EU'] == EU]
    if OriginatingPlatform2 != 'All OriginatingPlatform2':
        df_filtered = df_filtered[df_filtered['OriginatingPlatform2'] == OriginatingPlatform2]


      
    # Update the graph using the filtered data
    pv = pd.pivot_table(df_filtered, index=['routenameformatted'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    try:
    
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='bar-route')
    try:

        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='bar-route')
    try:

       trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='bar-route')


    return{
        'data':[trace1,trace2,trace3],
        'layout':
        go.Layout(
            title='Route-Wise Simbox detection status',
            barmode='stack',template=template,
            xaxis_title='Route Name',
            yaxis_title='Total Test')
    }
@app.callback(
    dash.dependencies.Output('FOPSOrginatingCountry', 'figure'),
    [dash.dependencies.Input('OrginatingCountry', 'value'),
    dash.dependencies.Input('date-picker-range', 'start_date'),
    dash.dependencies.Input('date-picker-range', 'end_date'),
    dash.dependencies.Input('template', 'value')])
def update_graph(OrginatingCountry,start_date, end_date,template):
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    # Filter the data based on the selected country
    if OrginatingCountry is None or OrginatingCountry == 'All OrginatingCountry':
        df_filtered = df
    else:
        df_filtered = df[df['OrginatingCountry'] == OrginatingCountry]

    # Create a pivot table with the filtered data
    pv = pd.pivot_table(df_filtered, index=['OrginatingNumber'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    try:
    
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='FOPSOrginatingCountry')
    try:

        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='FOPSOrginatingCountry')
    try:

       trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='FOPSOrginatingCountry')


    return{
        'data':[trace1,trace2,trace3],
        'layout':
        go.Layout(
            title='Route-Wise Simbox detection status',
            barmode='stack',template=template,
            xaxis_title='Orginating A_NumberSubscription',
            yaxis_title='Test')
    }
@app.callback(
    dash.dependencies.Output('schdulerchart', 'figure'),
    [dash.dependencies.Input('customer-name', 'value'),
    dash.dependencies.Input('date-picker-range', 'start_date'),
    dash.dependencies.Input('date-picker-range', 'end_date'),
    dash.dependencies.Input('template', 'value')])
def update_graph(customer_name,start_date, end_date,template):
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    # Filter the data based on the selected country
    if customer_name is None or customer_name == []:
        customer_name = 'All CUSTOMERID'
    if customer_name != 'All CUSTOMERID':
        df_filtered = df_filtered[df_filtered['CUSTOMERID'] == customer_name]

    # Create a pivot table with the filtered data
    pv = pd.pivot_table(df_filtered, index=['RequestorName'], columns=["SITEVerdict"], values=['tests'], aggfunc=sum, fill_value=0)
    try:
    
        trace1 = go.Bar(x=pv.index, y=pv[('tests', 'FAIL')], name='FAIL',text=pv[('tests', 'FAIL')],textposition='auto')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='schdulerchart')
    try:

        trace2 = go.Bar(x=pv.index, y=pv[('tests', 'INCONC')], name='INCON',text=pv[('tests', 'INCONC')],textposition='auto')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='schdulerchart')
    try:

       trace3 = go.Bar(x=pv.index, y=pv[('tests', 'PASS')], name='PASS',text=pv[('tests', 'PASS')],textposition='auto')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='schdulerchart')


    return{
        'data':[trace1,trace2,trace3],
        'layout':
        go.Layout(
            title='Customer-Wise Traffic status {}'.format(customer_name),
            barmode='stack',template=template,
            xaxis_title='Test Schedule by FPS-User',
            yaxis_title='Total Test')
    }

@app.callback(
    dash.dependencies.Output('Totaltest', 'figure'),
    [dash.dependencies.Input('template', 'value')])
def update_graph(template):
    # Create a pivot table with the filtered data
    pv = pd.pivot_table(df, columns=(df['DATE']),values=['Duration'], aggfunc=sum, fill_value=0)
    try:
        trace = go.Bar(x=pv.columns, y=pv.sum(axis=0), text=pv.sum(axis=0), textposition='auto')
    except:
        trace = go.Figure(data=[go.Bar(x=[], y=[])])
        trace.update_layout(title='Totaltest')
    return {
        'data': [trace],
        'layout': go.Layout(
            title='FPS - Total Duration Date-Wise',
            xaxis_title='Date',
            yaxis_title='Total Duration',
            template=template
        )
    }

@app.callback(
    dash.dependencies.Output('fopsduration', 'figure'),
    [dash.dependencies.Input('CallPick', 'value'),
     dash.dependencies.Input('Platform', 'value'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date'),
     dash.dependencies.Input('template', 'value')])
def update_graph(CallPick, Platform, start_date, end_date, template):
    # Filter the data based on the selected options and dates
    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    
    if CallPick is None or CallPick == []:
        CallPick = 'All CallPick'
    if Platform is None or Platform == []:
        Platform = 'All Platform'
    
    if CallPick != 'All CallPick':
        df_filtered = df_filtered[df_filtered['CallPickedUp'] == CallPick]
    if Platform != 'All Platform':
        df_filtered = df_filtered[df_filtered['OriginatingPlatform2'] == Platform]
      
    # Update the graph using the filtered data
    pv = pd.pivot_table(df_filtered, index=['CUSTOMERID'], columns=["SITEVerdict"], values=['Duration'], aggfunc=sum, fill_value=0)
    
    try:
        trace1 = go.Bar(x=pv.index, y=pv[('Duration', 'FAIL')], name='FAIL')
    except:
        trace1 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace1.update_layout(title='fopsduration')
    
    try:
        trace2 = go.Bar(x=pv.index, y=pv[('Duration', 'INCONC')], name='INCON')
    except:
        trace2 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace2.update_layout(title='fopsduration')
    
    try:
        trace3 = go.Bar(x=pv.index, y=pv[('Duration', 'PASS')], name='PASS')
    except:
        trace3 = go.Figure(data=[go.Bar(x=[], y=[])])
        trace3.update_layout(title='fopsduration')

    return {
        'data': [trace1, trace2, trace3],
        'layout': go.Layout(
            title='Destination wise Duration',
            barmode='stack',
            template=template,
            xaxis_title='Customer Name',
            yaxis_title='Sum Duration'
        )
    }



if __name__=='__main__':
    app.run_server(port=8083,debug=True,use_reloader=False)