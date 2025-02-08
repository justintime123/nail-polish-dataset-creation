import dash.exceptions

import pandas as pd
import plotly.express as px
import numpy as np
from config import PROCESSED_DATA_PATH
from dash import Dash, html, dcc, callback, Output, Input, dash_table

def get_data():
    df = pd.read_parquet(PROCESSED_DATA_PATH)
    keep_cols = ['brand', 'product_name', 'product_type', 'primary_finish', 'new_color', 'link']
    df = df[keep_cols]
    df.loc[(df['brand'] == 'Morgan Taylor')&(~df['link'].str.contains('http')), 'link'] = 'https://gelish.com' + df['link']
    df.loc[df['brand']=='OPI', 'link'] = 'https://opi.com' + df['link']
    df = df.rename(columns={'new_color': 'color', 'primary_finish': 'finish'})
    df = df.replace('', np.nan)
    return df

def get_bucketed_data(variable):
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
    data['bucket'] = np.where(data[variable].isna(), 'UNMAPPED', data['bucket'])

    bucket_col_name = f"{variable}_bucket"

    data = data.rename(columns={'bucket': bucket_col_name})

    return data


def get_double_bar_chart_by_variable(variable):

    data = get_bucketed_data(variable)

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

def get_pie_chart(brand, variable):
    data = get_bucketed_data(variable)
    data = data[data['brand']==brand]

    count_of_each_color = data.groupby(['brand', f"{variable}_bucket"])[f"{variable}_bucket"].count().reset_index(name='count')

    #https://stackoverflow.com/questions/72852058/python-how-to-plot-a-frequency-pie-chart-with-one-column-using-plotly-express
    #Apply groupby to dataframe, then pass in new df to px.pie
    fig = px.pie(count_of_each_color, values='count', names=f"{variable}_bucket",
                 color=f"{variable}_bucket",
                 color_discrete_map={'black (neutral)': 'black',
                                     'blue': 'cornflowerblue',
                                     'red': 'crimson',
                                     'orange': 'orange',
                                     'pink (light red)': 'pink',
                                     'gray (neutral)': 'lightgrey',
                                     'pink (magenta)': 'magenta',
                                     'yellow': 'yellow',
                                     'green': 'green',
                                     'purple': 'darkviolet',
                                     'white (neutral)': 'white',
                                     'OTHER': 'gray',
                                     'UNMAPPED': 'silver'
                                     },
                 title=brand)
    return fig

app = Dash()
app.title = 'Comparison of Nail Polish Attributes Between Brands'
app.layout = html.Div(children = [
    html.Div([
        html.Label(['Select attribute: '], style={'font-weight': 'bold'}),
        dcc.Dropdown(['color', 'finish'], 'color', id='dropdown', style={"width": "75%", 'margin-top':'8px'}),

        ]),
    html.Div(children=[
        dcc.Graph(figure={}, id='morgan_taylor_pie_chart', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(figure={}, id='opi_pie_chart', style={'width': '48%', 'margin-left': '4%', 'display': 'inline-block'}),
    ]),
    html.Div(children = [
        html.Div(id='morgan_taylor_table_container', style={'width': '48%', 'display': 'inline-block'}),
        html.Div(id='opi_table_container', style={'width': '48%', 'margin-left': '4%','display': 'inline-block'})
    ])
])

@callback(
    Output(component_id='morgan_taylor_pie_chart', component_property='figure'),
    Output(component_id='opi_pie_chart', component_property='figure'),
    Input(component_id='dropdown', component_property='value')
)
def update_pie_charts(val_chosen):
    return get_pie_chart('Morgan Taylor', val_chosen), get_pie_chart('OPI', val_chosen)

def update_dashtable(clickData, value, brand):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    bucket_selected = clickData["points"][0]["label"]
    df = get_bucketed_data(value)
    #filter dataframe according to selected category
    df = df[(df[f"{value}_bucket"]==bucket_selected) & (df['brand']==brand)]
    display_cols = ['product_name', 'color', 'finish', 'link']
    #display_cols = ['product_name', 'finish', 'product_type', f"{value}_bucket"]
    df = df[display_cols]
    #Modifying link column to match Markdown format, so it can be clickable
    df['link'] = '[Link]' + '(' + df['link'] + ')'
    df = df.rename(columns={'product_name': 'Product Name', 'color': 'Color', 'finish': 'Finish', 'link': 'Link'})
    table = dash_table.DataTable(data=df.to_dict('records'),
                                 columns=[
                                     {"id": col, "name": col, "presentation": "markdown"} if col=='Link' else {"id": col, "name": col} for col in df.columns
                                 ],
                                 markdown_options={"link_target": "_blank"}, #setting to open new tab when user clicks on link
                                 page_size=5,
                                 style_header={
                                     'backgroundColor': 'snow',
                                     'fontWeight': 'bold',
                                 },
                                 style_data = {},
                                 style_cell = {
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                 },
                                 css=[dict(selector="p", rule="margin: 0; text-align: center")],
                                 style_data_conditional=[
                                     {
                                        'if': {
                                            'column_id': 'Color',
                                            'filter_query': '{Color} is nil'
                                        },
                                         'backgroundColor': 'silver'
                                     }, {

                                        'if': {
                                             'column_id': 'Finish',
                                             'filter_query': '{Finish} is nil'
                                         },
                                         'backgroundColor': 'silver'
                                     }
                                 ]
                                 )

                                 # tooltip_header={'swatch_rgb_color': 'RGB value obtained from product image. This RGB value was mapped to a color'},
                                 # style_cell={'overflow': 'hidden',
                                 #             'textOverflow': 'ellipses',
                                 #             'maxWidth': 0},
                                 # tooltip_delay=0,
                                 # tooltip_duration=None)
    #TODO: Add hyperlinked emojis to link products
    return table


@callback(
    Output(component_id='morgan_taylor_table_container', component_property='children'),
    [Input(component_id='morgan_taylor_pie_chart', component_property='clickData'),
     Input(component_id='dropdown', component_property='value')]
)
def update_table(clickData, value):
    return update_dashtable(clickData, value, 'Morgan Taylor')

@callback(
    Output(component_id='opi_table_container', component_property='children'),
    [Input(component_id='opi_pie_chart', component_property='clickData'),
     Input(component_id='dropdown', component_property='value')]
)
def update_table(clickData, value):
    return update_dashtable(clickData, value, 'OPI')

# @callback(
#     Output(component_id='output_graph', component_property='figure'),
#     Input(component_id='dropdown', component_property='value')
# )
# def update_chart(val_chosen):
#     fig = get_double_bar_chart_by_variable(val_chosen)
#     return fig

#https://stackoverflow.com/questions/71320914/can-i-add-an-onclick-function-to-a-plotly-express-bar-chart
# @callback(
#     Output(component_id='table_container', component_property='children'),
#     [Input(component_id='output_graph', component_property='clickData'),
#      Input(component_id='dropdown', component_property='value')]
# )
# def update_table(clickData, value):
#     if not clickData:
#         raise dash.exceptions.PreventUpdate
#
#     bucket_selected = clickData["points"][0]["label"]
#     df = get_bucketed_data(value)
#     #filter dataframe according to selected category
#     df = df[df[f"{value}_bucket"]==bucket_selected]
#     table = dash_table.DataTable(data=df.to_dict('records'),
#                                  page_size=5)
#                                  # tooltip_header={'swatch_rgb_color': 'RGB value obtained from product image. This RGB value was mapped to a color'},
#                                  # style_cell={'overflow': 'hidden',
#                                  #             'textOverflow': 'ellipses',
#                                  #             'maxWidth': 0},
#                                  # tooltip_delay=0,
#                                  # tooltip_duration=None)
#     #TODO: Add hyperlinked emojis to link products
#     #TODO: change color of swatch_hex_colors using style_data_conditional and columns. Highlight cells with empty values
#     return table





if __name__=='__main__':
    #df = get_data()
    app.run(debug=True)
    #display_double_bar_chart_by_variable("new_color")
    #display_double_bar_chart_by_variable("primary_finish")
    # display_pie_chart('OPI', 'color')
