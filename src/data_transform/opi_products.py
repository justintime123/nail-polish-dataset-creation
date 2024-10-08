import pandas as pd

def transform_df(df):
    rename_cols = {'data-color-family-primary': 'color_family',
                   'data-color-finish': 'primary_finish',
                   'data-color-system': 'collection',
                   'product-type': 'product_type',
                   'product-name': 'product_name',
                   'href': 'link'}

    keep_cols = ['product_name', 'product_type', 'color_family', 'primary_finish', 'link']

    df = df.rename(columns=rename_cols)
    df = df[keep_cols]

    df['brand'] = 'OPI'
    #Color Foil polishes have mirror polishes
    #Fix missing entries in original data
    return df

def get_df():
    json_file = "../../data/opi_products_pages_1_thru_25.json"
    df = pd.read_json(json_file)
    df = transform_df(df)
    return df

if __name__=='__main__':
    df = get_df()
