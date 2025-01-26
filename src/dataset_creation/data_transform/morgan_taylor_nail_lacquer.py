#Finishes: I went thru the morgan_taylor_nail_lacquers data manually and noted finishes
#CREAM, PEARL, SHIMMER, SHEER, FROST?, GLITTER, HOLOGRAPHIC (plus glitter), METALLIC?,
#IRIDESCENT, OVERLAY COAT, SPECKLES, TRANSLUSCENT, MULTI DIMENSION, CHUNKY GLITTER
#Exceptions: All Tied Up .. with a Bow has both glitter and holographic
#Possible categories: CREAM, PEARL, SHIMMER, SHEER, TRANSLUCENT,
#GLITTER, CHUNKY GLITTER, HOLOGRAPHIC, MULTI DIMENSION, METALLIC, IRIDESCENT, FROST, NEON,
#OVERLAY COAT, SPECKLES

#To get... {color_detail} {finish_1} ... {color detail 2} {finish_2}

#Use regex to experiment with parsing using the above format
import pandas as pd
import os
import re
from src.dataset_creation.data_transform.tools.image_color_classification.image_color_classification import convert_rgb_color_to_color_family
from config import DATA_STEP_2

finishes = ['CRÈME', 'PEARL', 'SHIMMER', 'SHEER', 'TRANSLUCENT',
'GLITTER', 'CHUNKY GLITTER', 'HOLOGRAPHIC', 'METALLIC',
'IRIDESCENT', 'FROST', 'NEON','OVERLAY COAT', 'SPECKLES']
#TODO: took out MULTI DIMENSIONAL. Check if it's the same as MULTICHROME


def split_alt_text_into_desc(df):
    #https://stackoverflow.com/questions/6711971/regular-expressions-match-anything
    #https://stackoverflow.com/questions/18633334/regex-optional-group
    #https://stackoverflow.com/questions/60567595/regular-expression-treat-a-group-as-optional-if-its-not-present-but-if-present
    #First remove string before 'oz.'
    #Example: "Morgan Taylor Not So Prince Charming Nail Lacquer, 0.5 oz. BLUE CR&Egrave;ME"
    #Can remove using re.sub: https://stackoverflow.com/questions/30945784/how-to-remove-all-characters-before-a-specific-character-in-python
    df['alt_text_new'] = df['alt_text'].apply(lambda text: re.sub(r'^.*?(?:oz.|Disco Days Nail Lacquer)', '', text))
    #Replace 'CR&Egrave;ME' with 'Creme'
    df['alt_text_new'] = df['alt_text_new'].str.replace('CR&Egrave;ME','CRÈME')

    #Fixing exceptions to following regex
    df['alt_text_new'] = df['alt_text_new'].str.replace('DEEP PURPLE WITH SUBTLE PEARL','DEEP PURPLE PEARL')

    #Most alt_texts follow the below pattern
    # Meaning of regex:
    # Group 1: Color shade
    # Group 2: primary finish
    # Group 3: secondary finish
    df['split'] = df['alt_text_new'].apply(lambda x: re.findall(rf"^(.*?)\s({'|'.join(finishes)}).*?(\w+\s\w+)?$", x))

    #Exceptions
    #DEEP PURPLE WITH SUBTLE PEARL
    #Morgan Taylor Disco Days Nail Lacquer GREEN HOLOGRAPHIC -fixed
    #MULTI DIMENSIONAL ORANGE METALLIC -ignore
    #Different orders
    #LIGHT TRANSLUCENT PINK -ignore
    #SHEER PINK WITH SILVER FROST - can ignore
    #HOLOGRAPHIC PINK GLITTER    #https://www.reddit.com/r/lacqueristas/comments/18o42ch/help_with_polish_terminology/

    df['split'] = df['split'].apply(lambda x: x[0] if len(x) > 0 else ('','',''))
    #Split arguments into new columns
    #https://stackoverflow.com/questions/35491274/split-a-pandas-column-of-lists-into-multiple-columns
    #https://stackoverflow.com/questions/23317342/pandas-dataframe-split-column-into-multiple-columns-right-align-inconsistent-c

    #Using zip and * operator to assign new columns
    #https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
    #https://docs.python.org/3.3/library/functions.html#zip
    #Sequence unpacking: https://stackoverflow.com/questions/41530125/what-does-a-comma-do-in-a-python-assignment, https://stackoverflow.com/questions/11502268/how-does-pythons-comma-operator-work-during-assignment
    df['color_shade'], df['primary_finish'], df['secondary_finish'] = zip(*df['split'])

    #String formatting
    #https://stackoverflow.com/questions/22086619/how-to-apply-a-function-to-multiple-columns-in-a-pandas-dataframe-at-one-time
    df[['color_shade','primary_finish', 'secondary_finish']] = df[['color_shade','primary_finish', 'secondary_finish']].apply(lambda x: x.str.strip())
    df['product_type'] = 'Nail Lacquer'
    df['brand'] = 'Morgan Taylor'

    return df

def final_format(df):
    # needed_cols = ['brand', 'product_name', 'new_color_family', 'color_shade', 'primary_finish',
    #                'secondary_finish', 'original_description', 'link']
    #keep_cols = ['product_name', 'product_type', 'orig_color_family', 'new_color_family', 'primary_finish', 'link']
    keep_cols = ['brand','product_name', 'product_type', 'orig_color', 'new_color', 'dominant_rgb_color', 'primary_finish', 'link', 'time_collected']


    df['primary_finish'] = df['primary_finish'].str.upper()
    rename_cols = {'description': 'original_description',
                   'color_shade': 'orig_color',
                   'color_desc': 'orig_color'}

    df = df.rename(columns=rename_cols)

    df = df[keep_cols]

    return df


def get_lacquer_df():
    json_file = DATA_STEP_2 / "morgan_taylor_lacquer_polishes.parquet"
    df = pd.read_parquet(json_file)

    df['product_type'] = 'Nail Lacquer'
    #Parse alt_text for color shade, primary finish and secondary finish
    df = split_alt_text_into_desc(df)

    df = df.rename(columns = {'color_shade': 'orig_color'})
    df['new_color'] = df['dominant_rgb_color'].apply(lambda x: convert_rgb_color_to_color_family(str(x).split(",")))

    #Clean up dataframe and remove unneeded columns, to conform to data/df_format
    #I'm going to leave in the formatted alt_text, to show how 'color_shade', 'primary_finish' and 'secondary_finish' were derived
    #This could be good for data validation later on
    df = final_format(df)


    #TODO: fill in missing data

    return df

def split_desc_into_fields(df):
    #Make description field all upper-case
    df['description'] = df['description'].str.upper()
    df['split'] = df['description'].apply(lambda x: re.findall(rf"^(.*?)\s({'|'.join(finishes)})", x))

    df['split'] = df['split'].apply(lambda x: x[0] if len(x) > 0 else ('', ''))
    df['color_desc'], df['primary_finish'],  = zip(*df['split'])
    #TODO: Add Shimmer finish to 'Stop and Listen'
    return df

def get_vegan_df():
    json_file = DATA_STEP_2 / "morgan_taylor_vegan_polishes.parquet"
    df = pd.read_parquet(json_file)

    df['product_type'] = 'Vegan'

    #Parse description for color_description and finish
    df = split_desc_into_fields(df)

    #Convert dominant color into color value
    df['new_color'] = df['dominant_rgb_color'].apply(lambda x: convert_rgb_color_to_color_family(str(x).split(",")))

    df['brand'] = 'Morgan Taylor'

    df = final_format(df)

    return df

def get_df():
    vegan_df = get_vegan_df()
    lacquer_df = get_lacquer_df()
    df = pd.concat([vegan_df, lacquer_df])
    return df



if __name__ == '__main__':
    df = get_df()