from src.dataset_creation.data_transform import morgan_taylor_nail_lacquer, opi_products
import pandas as pd

def get_data():
    morgan_taylor = morgan_taylor_nail_lacquer.get_df()
    opi = opi_products.get_df()
    return pd.concat([morgan_taylor, opi])

if __name__=='__main__':
    df = get_data()
