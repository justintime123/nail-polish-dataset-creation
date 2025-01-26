from src.dataset_creation.data_transform import morgan_taylor_nail_lacquer, opi_products
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from config import PROCESSED_DATA_PATH
from dash import Dash, html, dcc, callback, Output, Input

def get_data():
    return pd.read_parquet(PROCESSED_DATA_PATH)

def display_double_bar_chart_by_variable(variable):
    data  = get_data()

    # group any categories that belong to one brand but not another in seperate "other" category
    unique_elems_opi = set(data[data['brand'] == 'OPI'][variable].unique())
    unique_elems_morgan_taylor = set(data[data['brand'] == 'Morgan Taylor'][variable].unique())
    #
    opi_other_bucket = unique_elems_opi - unique_elems_morgan_taylor  # What's in opi but not Morgan Taylor
    morgan_taylor_other_bucket = unique_elems_morgan_taylor - unique_elems_opi  # What's in morgan taylor but not Morgan Taylor
    #
    # #create new buckets
    other_values = opi_other_bucket | morgan_taylor_other_bucket
    data['bucket'] = np.where(data[variable].isin(other_values), 'OTHER', data[variable])

    #Add bucket for missing values
    data['bucket'] = np.where(data[variable]=='', 'UNMAPPED', data['bucket'])

    agg_data = data.groupby(['brand', 'bucket'])['bucket'].count().reset_index(name='count')

    #https://stackoverflow.com/questions/23377108/pandas-percentage-of-total-with-groupby
    agg_data['% of collection'] = 100 * agg_data['count']/agg_data.groupby('brand')['count'].transform('sum')
    agg_data['% of collection'] = agg_data['% of collection'].round(1)

    #set colors of each bar
    color_discrete_map={'Morgan Taylor': '#B049B6', 'OPI': '#4FB649'}
    fig = px.bar(agg_data, x='bucket', y='% of collection', color='brand', barmode='group', title=variable + " distribution", color_discrete_map=color_discrete_map)

    #Make bars descending order
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    #fig.show()
    # fig = px.bar(data, x='new_color', y='count')
    #fig = go.Figure()
    #fig.add_trace(go.Histogram(histfunc="count", x=data[variable], color="brand"))
    fig.show()

def display_pie_chart():
    data = get_data()
    #https://stackoverflow.com/questions/72852058/python-how-to-plot-a-frequency-pie-chart-with-one-column-using-plotly-express
    #Apply groupby to dataframe, then pass in new df to px.pie
    opi = data[data['brand']=='OPI']
    count_of_each_color = opi.groupby(['new_color'])['new_color'].count().reset_index(name='count')
    fig = px.pie(count_of_each_color, values='count', names='new_color', title='Breakdown by Color')
    fig.show()


if __name__=='__main__':
    display_double_bar_chart_by_variable("new_color")
    #display_double_bar_chart_by_variable("primary_finish")
    #display_pie_chart()
