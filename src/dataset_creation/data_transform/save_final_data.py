import morgan_taylor_nail_lacquer
import opi_products
import pandas as pd
from config import PROCESSED_DATA_PATH

def get_data():
    morgan_taylor = morgan_taylor_nail_lacquer.get_df()
    opi = opi_products.get_df()
    return pd.concat([morgan_taylor, opi])

def save_data():
    df = get_data()
    df.to_parquet(PROCESSED_DATA_PATH)

if __name__ == '__main__':
    save_data()