import pandas as pd
from src.dataset_creation.data_transform.tools.image_color_classification.image_color_classification import convert_rgb_color_to_color_family


def transform_df(df):
    rename_cols = {'data-color-family-primary': 'orig_color_family',
                   'data-color-finish': 'primary_finish',
                   'data-color-system': 'collection',
                   'product-type': 'product_type',
                   'product-name': 'product_name',
                   'href': 'link'}

    keep_cols = ['product_name', 'product_type', 'orig_color_family', 'new_color_family', 'primary_finish', 'link']

    df = df.rename(columns=rename_cols)
    df = df[keep_cols]

    df['brand'] = 'OPI'
    #Color Foil polishes have mirror polishes
    #Fix missing entries in original data
    return df

def get_df():
    json_file = "../../data/step_2/opi_products.parquet"
    df = pd.read_parquet(json_file)

    # Convert dominant color into color value
    df['new_color_family'] = df['dominant_rgb_color'].apply(
        lambda x: convert_rgb_color_to_color_family(str(x).split(",")))

    df = transform_df(df)

    return df

if __name__=='__main__':
    df = get_df()
