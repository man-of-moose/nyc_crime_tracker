# nyc_crime_tracker

## Data Source:

This project uses data sourced from Data.gov. The dataset, "NYPD Arrests Data", contains information about every arrest in NYC dating back to 2006. In total, there are over 5 million entries in the dataset.
For this project, initial data transformations and cleaning occur in the .ipynb notebook, "Data Processing". The data processing steps include formatting missing values, and removing data earlier than 2019 in order to streamline the online dash application.
Future iterations of this project will explore alternate methods to include all data back to 2006.

URL: https://catalog.data.gov/dataset/nypd-arrests-data-historic

## Available Parameters:

The dataset includes the following parameters:

  ['ARREST_KEY, 'ARREST_DATE', 'PD_CD', 'PD_DESC', 'KY_CD', 'OFNS_DESC', 'LAW_CODE', 'LAW_CAT_CD', 'ARREST_BORO', 'ARREST_PRECINCT',
       'JURISDICTION_CODE', 'AGE_GROUP', 'PERP_SEX', 'PERP_RACE', 'X_COORD_CD', 'Y_COORD_CD', 'Latitude', 'Longitude', 'Lon_Lat']
       
       
## Importance of Data

A crime dashboard covering all crimes in NYC from 2006-2021 is extremely relevant for many parties - including Civilians, Police, Government Officials, Non-Profits, etc - to better understand current crime trends in NYC. This kind of information allows individuals to better prepare for the inherent criminal risk involved in living in a major metropolis. City planners likewise are better equiped to create equitable and effective laws intended to treat crime in the city.


## Technologies Used

Plotly, Datashader, Dash, Heroku
