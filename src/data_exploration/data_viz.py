import dash.exceptions

from src.dataset_creation.data_transform import morgan_taylor_nail_lacquer, opi_products
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from config import PROCESSED_DATA_PATH
from dash import Dash, html, dcc, callback, Output, Input, dash_table

def get_data():
    df = pd.read_parquet(PROCESSED_DATA_PATH)
    keep_cols = ['brand', 'product_name', 'product_type', 'primary_finish', 'new_color']
    df = df[keep_cols]
    df = df.rename(columns={'new_color': 'color', 'primary_finish': 'finish'})
    return df

def get_bar_chart_data(variable):
    data = get_data()

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

    # Add bucket for missing values
    data['bucket'] = np.where(data[variable] == '', 'UNMAPPED', data['bucket'])

    bucket_col_name = f"{variable}_bucket"

    data = data.rename(columns={'bucket': bucket_col_name})

    return data


def get_double_bar_chart_by_variable(variable):

    data = get_bar_chart_data(variable)

    agg_data = data.groupby(['brand', f"{variable}_bucket"])[f"{variable}_bucket"].count().reset_index(name='count')

    #https://stackoverflow.com/questions/23377108/pandas-percentage-of-total-with-groupby
    agg_data['% of collection'] = 100 * agg_data['count']/agg_data.groupby('brand')['count'].transform('sum')
    agg_data['% of collection'] = agg_data['% of collection'].round(1)

    #set colors of each bar
    color_discrete_map={'Morgan Taylor': '#B049B6', 'OPI': '#4FB649'}
    fig = px.bar(agg_data, x=f"{variable}_bucket", y='% of collection', color='brand', barmode='group', color_discrete_map=color_discrete_map)

    #Make bars descending order
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    #fig.show()
    # fig = px.bar(data, x='new_color', y='count')
    #fig = go.Figure()
    #fig.add_trace(go.Histogram(histfunc="count", x=data[variable], color="brand"))
    return fig

def display_pie_chart():
    data = get_data()
    #https://stackoverflow.com/questions/72852058/python-how-to-plot-a-frequency-pie-chart-with-one-column-using-plotly-express
    #Apply groupby to dataframe, then pass in new df to px.pie
    opi = data[data['brand']=='OPI']
    count_of_each_color = opi.groupby(['color'])['color'].count().reset_index(name='count')
    fig = px.pie(count_of_each_color, values='count', names='color', title='Breakdown by Color')
    fig.show()

app = Dash()
app.layout = html.Div(children = [
    html.H1(children='Comparison of Nail Polish Attributes Between Brands'),
    html.Div(children='Select attribute below:'),
    dcc.Dropdown(['color', 'finish'], 'color', id='dropdown'),
    dcc.Graph(figure={}, id='output_graph'),
    html.Div(id='table_container')
])

@callback(
    Output(component_id='output_graph', component_property='figure'),
    Input(component_id='dropdown', component_property='value')
)
def update_chart(val_chosen):
    fig = get_double_bar_chart_by_variable(val_chosen)
    return fig

#https://stackoverflow.com/questions/71320914/can-i-add-an-onclick-function-to-a-plotly-express-bar-chart
@callback(
    Output(component_id='table_container', component_property='children'),
    [Input(component_id='output_graph', component_property='clickData'),
     Input(component_id='dropdown', component_property='value')]
)
def update_table(clickData, value):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    bucket_selected = clickData["points"][0]["label"]
    df = get_bar_chart_data(value)
    #filter dataframe according to selected category
    df = df[df[f"{value}_bucket"]==bucket_selected]
    table = dash_table.DataTable(data=df.to_dict('records'),
                                 page_size=5)
                                 # tooltip_header={'swatch_rgb_color': 'RGB value obtained from product image. This RGB value was mapped to a color'},
                                 # style_cell={'overflow': 'hidden',
                                 #             'textOverflow': 'ellipses',
                                 #             'maxWidth': 0},
                                 # tooltip_delay=0,
                                 # tooltip_duration=None)
    #TODO: Add hyperlinked emojis to link products
    #TODO: change color of swatch_hex_colors using style_data_conditional and columns. Highlight cells with empty values
    return table





if __name__=='__main__':
    #df = get_data()
    app.run(debug=True)
    #display_double_bar_chart_by_variable("new_color")
    #display_double_bar_chart_by_variable("primary_finish")
    #display_pie_chart()
