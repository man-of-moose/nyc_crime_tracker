import pandas as pd
import plotly.graph_objects as go # or plotly.express as px
import dash
import datashader as ds
from colorcet import fire
import datashader.transfer_functions as tf
import plotly.express as px
import time

from dash import callback
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import chart_studio.plotly as py
import plotly.graph_objs as go
import numpy as np
import json
import copy
import xarray as xr
from collections import OrderedDict

dash.register_page(__name__)

## load and clean data
dff = pd.read_csv('https://raw.githubusercontent.com/man-of-moose/new_final_608/master/reduced_2019_plus_primary.csv')
dff = dff.fillna("MISSING DATA")
# dff = pd.read_csv("reduced2.csv")
dff['ARREST_DATE'] = pd.to_datetime(dff['ARREST_DATE'])

#####

original = ['MISSING DATA','RAPE','SEX CRIMES','ARSON','FORGERY','ASSAULT 3 & RELATED OFFENSES','FELONY ASSAULT','ANTICIPATORY OFFENSES','ROBBERY','MISCELLANEOUS PENAL LAW','DANGEROUS DRUGS','PETIT LARCENY','DANGEROUS WEAPONS','CRIMINAL TRESPASS','FRAUDS','OFFENSES INVOLVING FRAUD','BURGLARY','OFFENSES AGAINST PUBLIC ADMINI','VEHICLE AND TRAFFIC LAWS','JOSTLING','DISORDERLY CONDUCT','POSSESSION OF STOLEN PROPERTY','GRAND LARCENY','CRIMINAL MISCHIEF & RELATED OF','FOR OTHER AUTHORITIES','INTOXICATED & IMPAIRED DRIVING','ALCOHOLIC BEVERAGE CONTROL LAW','UNAUTHORIZED USE OF A VEHICLE','NYS LAWS-UNCLASSIFIED FELONY','OTHER OFFENSES RELATED TO THEF','THEFT OF SERVICES','HOMICIDE-NEGLIGENTUNCLASSIFIE','OFF. AGNST PUB ORD SENSBLTY &','OTHER TRAFFIC INFRACTION','"BURGLARS TOOLS"','PROSTITUTION & RELATED OFFENSES','CHILD ABANDONMENT/NON SUPPORT','INTOXICATED/IMPAIRED DRIVING','GAMBLING','OTHER STATE LAWS (NON PENAL LA','GRAND LARCENY OF MOTOR VEHICLE','OTHER STATE LAWS','MURDER & NON-NEGL. MANSLAUGHTE','ADMINISTRATIVE CODE','THEFT-FRAUD','OFFENSES AGAINST PUBLIC SAFETY','AGRICULTURE & MRKTS LAW-UNCLASSIFIED','OFFENSES AGAINST THE PERSON','HARRASSMENT 2','ADMINISTRATIVE CODES','KIDNAPPING & RELATED OFFENSES','MOVING INFRACTIONS','KIDNAPPING AND RELATED OFFENSES','HOMICIDE-NEGLIGENT-VEHICLE','OFFENSES RELATED TO CHILDREN','OTHER STATE LAWS (NON PENAL LAW)','ENDAN WELFARE INCOMP','FRAUDULENT ACCOSTING','ESCAPE 3','KIDNAPPING','LOITERING/GAMBLING (CARDS DIC','LOITERING FOR DRUG PURPOSES','NEW YORK CITY HEALTH CODE','PARKING OFFENSES','UNLAWFUL POSS. WEAP. ON SCHOOL','DISRUPTION OF A RELIGIOUS SERV','NYS LAWS-UNCLASSIFIED VIOLATION','FELONY SEX CRIMES']
grouping = ['MISSING','SEX CRIMES','SEX CRIMES','ARSON','FRAUD','ASSAULT','ASSAULT','OTHER','THEFT','OTHER','DRUGS / ALCOHOL','THEFT','WEAPONS','TRESPASSING','FRAUD','FRAUD','THEFT','OTHER','VEHICLE / DUI','OTHER','PUBLIC SAFETY','THEFT','THEFT','OTHER','OTHER','VEHICLE / DUI','DRUGS / ALCOHOL','VEHICLE / DUI','OTHER','THEFT','THEFT','HOMICIDE','OTHER','VEHICLE / DUI','THEFT','PROSTITUTION','CHILD ABUSE','VEHICLE / DUI','GAMBLING','OTHER','THEFT','OTHER','HOMICIDE','OTHER','THEFT','PUBLIC SAFETY','OTHER','ASSAULT','HARASSMENT','OTHER','KIDNAPPING','VEHICLE / DUI','KIDNAPPING','VEHICLE / DUI','CHILD ABUSE','OTHER','OTHER','FRAUD','OTHER','KIDNAPPING','GAMBLING','DRUGS / ALCOHOL','HEALTH VIOLATION','VEHICLE / DUI','WEAPONS','PUBLIC SAFTEY','OTHER','SEX CRIMES']

zipped = list(zip(original, grouping))
mapper = {}
for pair in zipped:
    
    key = pair[0]
    value = pair[1]
    
    mapper[key] = value

dff['OFNS_DESC'] = dff['OFNS_DESC'].map(mapper)

######


daterange = pd.date_range(start=dff['ARREST_DATE'].min(),end=dff['ARREST_DATE'].max(),freq='W')

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(start, end, Nth=10):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

crime_count = dff.groupby(['OFNS_DESC'])['ARREST_DATE'].count().reset_index().sort_values(by=['ARREST_DATE'], ascending=False)['OFNS_DESC'].unique()
boros = dff['ARREST_BORO'].unique()
crimes = dff['OFNS_DESC'].unique()


ny_census = {
    "AMERICAN INDIAN/ALASKAN NATIVE":0.025,
    "ASIAN / PACIFIC ISLANDER":0.156,
    "BLACK":0.202,
    "BLACK HISPANIC":0.09905,
    "UNKNOWN":0.025,
    "WHITE":0.309,
    "WHITE HISPANIC":0.18395
}


def generate_image(input_df):
    cvs2 = ds.Canvas(plot_width=1000, plot_height=1000)
    agg = cvs2.points(input_df, x='Longitude', y='Latitude')
    # agg is an xarray object, see http://xarray.pydata.org/en/stable/ for more details
    coords_lat, coords_lon = agg.coords['Latitude'].values, agg.coords['Longitude'].values
    # Corners of the image, which need to be passed to mapbox
    coordinates = [[coords_lon[0], coords_lat[0]],
                [coords_lon[-1], coords_lat[0]],
                [coords_lon[-1], coords_lat[-1]],
                [coords_lon[0], coords_lat[-1]]]


    img2 = tf.shade(agg, cmap=fire)[::-1].to_pil()

    # Trick to create rapidly a figure with mapbox axes
    fig = px.scatter_mapbox(input_df[:1], 
                            lat='Latitude', 
                            lon='Longitude', 
                            zoom=10, width=1400, height = 600)
    # Add the datashader image as a mapbox layer image
    fig.update_layout(mapbox_style="carto-positron",
                    mapbox_layers = [
                    {
                        "sourcetype": "image",
                        "source": img2,
                        "coordinates": coordinates
                    }]
    )

    fig.update_traces(marker={'size': 1})

    return fig



layout = html.Div(children=[
    #html.P('Search for crimes by boro, time'),
    html.H4(children='Select Borough and Crime'),

    dcc.Checklist(
        id='dropdown_a',
        options=[{'label': i, 'value': i} for i in boros],
        value=['M','B','Q','K','S'],
        inline=True
    ),
    html.Br(),
    dcc.Checklist(
        id='dropdown_b',
        options=[{'label': i, 'value': i} for i in crime_count],
        value=['ASSAULT'],
        inline=True
    ),
    html.Br(),
    dcc.RangeSlider(
                id='year_slider',
                min = unixTimeMillis(daterange.min()),
                max = unixTimeMillis(daterange.max()),
                value = [unixTimeMillis(daterange.min()),
                         unixTimeMillis(daterange.max())],
                marks=getMarks(daterange.min(),
                            daterange.max())
            ),
    
    html.Br(),
    html.Div(id='output_a'),
    
    html.H2(children='Trend over Time'),
    html.Div(id='output_b'),

    html.Div([
        html.H2(children='Demographic Distributions'),
        html.Div(children=[
            html.Div(id='output_c', style={'display': 'inline-block'}),
            html.Div(id='output_d', style={'display': 'inline-block'}),
            html.Div(id='output_e', style={'display': 'inline-block'}),
            html.Div(id='output_f', style={'display': 'inline-block'}),
            ])
        ]),
    html.Br(),
    html.Br(),
])

## Map

@callback(
    Output(component_id='output_a', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value'),
        Input(component_id = 'year_slider', component_property = 'value')
    ]
)
def boro_graph(dropdown_a, dropdown_b, year_slider):
    new_df = dff[
                (dff['ARREST_BORO'].isin(dropdown_a)) & 
                (dff['OFNS_DESC'].isin(dropdown_b)) &
                (dff['ARREST_DATE'] > unixToDatetime(year_slider[0])) &
                (dff['ARREST_DATE'] < unixToDatetime(year_slider[1]))
                ]

    return dcc.Graph(
        id='Select Borough and Crime',
        figure=generate_image(new_df)
    )

## Line Chart

@callback(
    Output(component_id='output_b', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value'),
        Input(component_id = 'year_slider', component_property = 'value')
    ]
)
def update_line_chart(dropdown_a, dropdown_b, year_slider):
    new_df = dff[
                (dff['ARREST_BORO'].isin(dropdown_a)) & 
                (dff['OFNS_DESC'].isin(dropdown_b)) &
                (dff['ARREST_DATE'] > unixToDatetime(year_slider[0])) &
                (dff['ARREST_DATE'] < unixToDatetime(year_slider[1]))
                ]

    aggregate = new_df.groupby(['ARREST_DATE'])['OFNS_DESC'].count().reset_index()

    fig = px.line(aggregate, 
        x="ARREST_DATE", y="OFNS_DESC")

    return dcc.Graph(
        id='Over Time',
        figure=fig
    )

## Side by Side Chart

@callback(
    Output(component_id='output_c', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value')
    ]
)

def agegroup_chart(dropdown_a, dropdown_b):
    new_df = dff[(dff['ARREST_BORO'].isin(dropdown_a)) & (dff['OFNS_DESC'].isin(dropdown_b))]
    new_df = new_df.sort_values(by=['AGE_GROUP'])

    return dcc.Graph(
        id='Demographic Distributions',
        figure={
            'data': [
                {'x': new_df['AGE_GROUP'], 'type': 'histogram'}
            ],
            'layout': {
                'title': "Crime by Age"
            }
        }
    )

@callback(
    Output(component_id='output_d', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value')
    ]
)

def agegroup_chart(dropdown_a, dropdown_b):
    new_df = dff[(dff['ARREST_BORO'].isin(dropdown_a)) & (dff['OFNS_DESC'].isin(dropdown_b))]
    new_df = new_df.sort_values(by=['PERP_SEX'])

    return dcc.Graph(
        id='Demographic Distributions',
        figure={
            'data': [
                {'x': new_df['PERP_SEX'], 'type': 'histogram'}
            ],
            'layout': {
                'title': "Crime by Sex"
            }
        }
    )

@callback(
    Output(component_id='output_e', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value')
    ]
)

def agegroup_chart(dropdown_a, dropdown_b):
    new_df = dff[(dff['ARREST_BORO'].isin(dropdown_a)) & (dff['OFNS_DESC'].isin(dropdown_b))]
    new_df = new_df.sort_values(by=['PERP_RACE'])

    return dcc.Graph(
        id='Demographic Distributions',
        figure={
            'data': [
                {'x': new_df['PERP_RACE'], 'type': 'histogram'}
            ],
            'layout': {
                'title': "Crime by Race"
            }
        }
    )

@callback(
    Output(component_id='output_f', component_property='children'),
    [
        Input(component_id = 'dropdown_a', component_property = 'value'),
        Input(component_id = 'dropdown_b', component_property = 'value'),
        Input(component_id = 'year_slider', component_property = 'value')
    ]
)
def update_line_chart(dropdown_a, dropdown_b, year_slider):
    new_df = dff[
                (dff['ARREST_BORO'].isin(dropdown_a)) & 
                (dff['OFNS_DESC'].isin(dropdown_b)) &
                (dff['ARREST_DATE'] > unixToDatetime(year_slider[0])) &
                (dff['ARREST_DATE'] < unixToDatetime(year_slider[1]))
                ]

    crime_group = new_df.groupby(['PERP_RACE'])['ARREST_KEY'].count()
    crime_rates = crime_group / sum(crime_group)

    ratio = {}
    for key, value in ny_census.items():
        crime_value = crime_rates[key]
        new_val = (crime_value - value) / value
        ratio[key] = new_val

    ratio_df = pd.DataFrame(pd.Series(ratio)).reset_index()
    ratio_df.columns = ['Race','Policing Index']

    fig = px.bar(ratio_df, 
        x="Race", y="Policing Index")

    return dcc.Graph(
        id='Demographic Distributions',
        figure=fig
    )