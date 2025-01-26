import pandas as pd
from src.dataset_creation.data_transform.tools.image_color_classification.image_color_classification import convert_rgb_color_to_color_family
from config import DATA_STEP_2


def transform_df(df):
    rename_cols = {'data-color-family-primary': 'orig_color',
                   'data-color-finish': 'primary_finish',
                   'data-color-system': 'collection',
                   'product-type': 'product_type',
                   'product-name': 'product_name',
                   'href': 'link'}

    keep_cols = ['brand', 'product_name', 'product_type', 'orig_color', 'new_color', 'dominant_rgb_color', 'primary_finish', 'link', 'time_collected']

    df = df.rename(columns=rename_cols)
    df = df[keep_cols]

    df['primary_finish'] = df['primary_finish'].str.upper()

    df.loc[df['primary_finish']=='CREME', 'primary_finish'] = 'CRÈME'



    return df

def get_df():
    json_file = DATA_STEP_2 / "opi_products.parquet"
    df = pd.read_parquet(json_file)

    # Convert dominant color into color value
    df['new_color'] = df['dominant_rgb_color'].apply(
        lambda x: convert_rgb_color_to_color_family(str(x).split(",")))

    df['brand'] = 'OPI'
    #TODO: Color Foil polishes have mirror polishes
    #TODO: Fix missing entries in original data

    df = transform_df(df)

    return df

if __name__=='__main__':
    df = get_df()
