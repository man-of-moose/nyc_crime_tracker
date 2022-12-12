import dash
from dash import html, dcc, callback, Output, Input
import pandas as pd
from dash import dash_table

dash.register_page(__name__, path='/')

## load and clean data
dff = pd.read_csv('https://raw.githubusercontent.com/man-of-moose/new_final_608/master/reduced_2019_plus_primary.csv')
dff = dff.fillna("MISSING DATA")
# dff = pd.read_csv("reduced2.csv")
dff['ARREST_DATE'] = pd.to_datetime(dff['ARREST_DATE'])

data_table_df = dff.head(100).sample(frac=1)[['ARREST_DATE','OFNS_DESC','ARREST_BORO','AGE_GROUP',
                                    'PERP_SEX','PERP_RACE','Latitude','Longitude']]

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

boros = dff['ARREST_BORO'].unique()

layout = html.Div(children=[
    html.H4(children='Summary of Data Utilized'),


    html.Div([
        html.P(''''
        List of every arrest in NYC going back to 2006 through the end of the previous calendar year. 
        This is a breakdown of every arrest effected in NYC by the NYPD going back to 2006 through the 
        end of the previous calendar year. This data is manually extracted every quarter and reviewed by 
        the Office of Management Analysis and Planning before being posted on the NYPD website. Each 
        record represents an arrest effected in NYC by the NYPD and includes information about the type of 
        crime, the location and time of enforcement. In addition, information related to suspect 
        demographics is also included. This data can be used by the public to explore the nature of police 
        enforcement activity. Please refer to the attached data footnotes for additional information 
        about this dataset.
        ''')
        ]),

    dash_table.DataTable(data_table_df.to_dict('records'),
                        [{"name": i, "id": i} for i in data_table_df.columns], 
                        id='tbl',
                        style_table={
                            'overflowY':'auto',
                            'height':200
                        },
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white'
                        },
                        style_data={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white'
                        },
            ),

    html.Br(),
    dcc.Checklist(
        id='boro_dropdown',
        options=[{'label': i, 'value': i} for i in boros],
        value=['M'],
        inline=True
    ),
    html.Br(),
    html.H2(children='Top Crimes by Borough'),
    html.Div(id='summary_bar')

])

@callback(
    Output(component_id='summary_bar', component_property='children'),
    [
        Input(component_id = 'boro_dropdown', component_property = 'value'),
    ]
)

def agegroup_chart(boro_dropdown):
    new_df = dff[dff['ARREST_BORO'].isin(boro_dropdown)]
    new_df = new_df.sort_values(by=['OFNS_DESC'])

    return dcc.Graph(
        id='Top Crimes by Borough',
        figure={
            'data': [
                {'x': new_df['OFNS_DESC'], 'type': 'histogram'}
            ]
            # 'layout': {
            #     'title': "Top Crimes per Boro"
            # }
        }
    )
