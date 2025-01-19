import pandas as pd
import os

def transform_df():
    #TODO: Join all category filter sections on Polish Name

    #Color Foil polishes have mirror polishes
    #Fix missing entries in original data
    return

def get_df():
    json_file = "../../../../data/sally_hansen_products_by_filter.json"
    df = pd.read_json(json_file)
    return df

if __name__=='__main__':
    df = get_df()

