#Finishes: I went thru the morgan_taylor_nail_lacquers data manually and noted finishes
#CREAM, PEARL, SHIMMER, SHEER, FROST?, GLITTER, HOLOGRAPHIC (plus glitter), METALLIC?,
#IRIDESCENT, OVERLAY COAT, SPECKLES, TRANSLUSCENT, MULTI DIMENSION, CHUNKY GLITTER
#Exceptions: All Tied Up .. with a Bow has both glitter and holographic
#Possible categories: CREAM, PEARL, SHIMMER, SHEER, TRANSLUCENT,
#GLITTER, CHUNKY GLITTER, HOLOGRAPHIC, MULTI DIMENSION, METALLIC, IRIDESCENT, FROST, NEON,
#OVERLAY COAT, SPECKLES

#To get... {color_detail} {finish_1} ... {color detail 2} {finish_2}

#Use regex to experiment with parsing using the above format
import re
import pandas as pd
import os
import re

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
    needed_cols = ['brand', 'product_name', 'product_type', 'color_family', 'color_shade', 'primary_finish',
                   'secondary_finish', 'original_description', 'link']

    rename_cols = {'color': 'color_family',
                   'alt_text_new': 'original_description'}

    df = df.rename(columns=rename_cols)

    df = df[needed_cols]

    return df


def get_lacquer_df():
    json_file = "../../data/morgan_taylor_nail_lacquers.json"
    df = pd.read_json(json_file)
    #Parse alt_text for color shade, primary finish and secondary finish
    df = split_alt_text_into_desc(df)

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
    #TODO: Add Shimmer finish to 'Stop and Listen'
    return df

def get_top_rgb_value(colors_by_percent):
    #TODO: Improve process by returning subset of colors_by_percent that make up some % amount of composition
    # percent = 0.90
    #add colors to percentile until percent covered >= percent
    #Put glitter in its own category
    return colors_by_percent[0][1]

def get_color_name(rgb):
    # rgb_colors_by_family = {
    #     'purple':
    #         {
    #             'periwinkle': (204,204,255),
    #             'dark purple': (52,21,57),
    #             'purple': (157,0,255)
    #         },
    #     'pink': {
    #         'light pink': (255,181,192),
    #         'pink': (255,141,161),
    #         'hot pink': (255,70,162)
    #
    #     },
    #     'red':
    #         {'red': (255,44,44),
    #          'maroon': (85,0,0),
    #          'burgundy': (102,0,51)
    #          },
    #     'orange':
    #         {'orange': (255,165,0),
    #          'nude': (247,217,188),
    #          'coral': (255,133,89)},
    #     'yellow':
    #         {'yellow': (255,222,33),
    #          'gold': (239,191,4)},
    #     'green':
    #         {'green': (0,128,0)},
    #     'blue':
    #         {'blue': (0,0,255)},
    #     'neutrals': #for pure neutrals, R,G and B channels are equal
    #         {'light gray': (211,211,211),
    #          'rose gold': (222,161,147),
    #          'brown': (137,81,41),
    #          'off-white': (242,240,239),
    #          'black': (0,0,0)
    #          }
    # }
    #  'purple': (157, 0, 255),
    #     'periwinkle': (204, 204, 255),
    #     'dark purple': (52, 21, 57),
    #     'light pink': (255, 181, 192),
    #     'pink': (255, 141, 161),
    #     'hot pink': (255, 70, 162),
    #     'fuscia': (255,0,255),
    #     'red': (255, 44, 44),
    #     'maroon': (85, 0, 0),
    #     'burgundy': (102,0,51),
    #     'orange': (255, 165, 0),
    #     #'nude orange': (247, 217, 188),
    #     'coral': (255, 133, 89),
    #     'yellow': (255, 222, 33),
    #     'gold': (239, 191, 4),
    #     'green': (0, 128, 0),
    #     'blue': (0, 0, 255),
    rgb_colors_by_family = {
       'red': (255,0,0),
        'rose': (255,0,128),
        'magenta': (255,0,255),
        'violet': (128,0,255),
        'dark purple': (52, 21, 57),
        'blue': (0,0,255),
        'azure': (0,128,255),
        'cyan': (0,255,255),
        'spring green': (0,255,128),
        'green': (0,255,0),
        'chartreuse': (128, 255, 0),
        'yellow': (255,255,0),
        'orange': (255,128,0)}
        # 'light gray': (211, 211, 211),
        # 'rose gold': (222, 161, 147),
        # 'brown': (137, 81, 41),
        # 'off-white': (242, 240, 239),
        # 'black': (0, 0, 0)


    # algorithm to match closest color using Euclidean distance
    # Src: https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green-with-python

    #For pure neutrals, R=G=B
    #For near neutrals, r,g and b values are close to each other
    #For simplicity, I'll define near-neutrals as when r,g and b values are within 50 values of each other

    #Neutral test
    r_g_distance = abs(rgb[0] - rgb[1])
    r_b_distance = abs(rgb[0] - rgb[2])
    b_g_distance = abs(rgb[1] - rgb[2])
    if r_g_distance<=55 and r_b_distance<=55 and b_g_distance<=55:
        return 'neutral'

    #If not, test for non-neutral categories
    names_by_distance = {}
    for name, rgb_value in rgb_colors_by_family.items():
        r_c, g_c, b_c = rgb_value
        r_distance = (r_c - rgb[0]) ** 2
        g_distance = (g_c - rgb[1]) ** 2
        b_distance = (b_c - rgb[2]) ** 2
        euclidean_distance = r_distance + g_distance + b_distance
        names_by_distance[(euclidean_distance)] = name

    #Return color name corresponding to minimum distance
    return names_by_distance[min(names_by_distance.keys())]


def get_color_family(df):
    #https://www.figma.com/colors

    df['top_color_rgb'] =  df['top_colors_by_percent'].apply(lambda x: get_top_rgb_value(x))
    df['top_color_name'] = df['top_color_rgb'].apply(lambda x: get_color_name(x))
    # For each polish, use rgb concentrations in swatch picture to determine closest match to color values in lacquer:
    color_list = ['purple', 'pink', 'red', 'orange'', coral', 'yellow', 'green', 'blue', 'neutrals', 'metallic',
                  'glitter']

    return df


def get_vegan_df():
    json_file = "../../data/morgan_taylor_vegan_polishes.json"
    df = pd.read_json(json_file)

    #Parse description for color_description and finish
    df = split_desc_into_fields(df)

    #Remove top coat from list
    #Convert top_colors_per_percent into a color_family
    df = get_color_family(df)

    return df



if __name__ == '__main__':
    print(os.getcwd())
    #dir = "../data'
    #dir = "/Users/justinchassin/PycharmProjects/nailPolishProj"
    df = get_vegan_df()
    pass