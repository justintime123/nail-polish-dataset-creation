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

finishes = ['CR&Egrave;ME', 'PEARL', 'SHIMMER', 'SHEER', 'TRANSLUCENT',
'GLITTER', 'CHUNKY GLITTER', 'HOLOGRAPHIC', 'METALLIC',
'IRIDESCENT', 'FROST', 'NEON','OVERLAY COAT', 'SPECKLES']
#TODO: took out MULTI DIMENSIONAL. Check if it's the same as MULTICHROME


def split_alt_text_into_desc(df):
    #https://stackoverflow.com/questions/6711971/regular-expressions-match-anything
    #https://stackoverflow.com/questions/18633334/regex-optional-group
    #https://stackoverflow.com/questions/60567595/regular-expression-treat-a-group-as-optional-if-its-not-present-but-if-present
    #for simple cases, the below would work:
    #re.findall(rf"(.*)\s({'|'.join(finishes)})", "LIGHT PINK SHIMMER")
    #re.findall(rf"(.*)\s({'|'.join(finishes)})\s?(.*)?", "RED GLITTER WITH A HINT OF SILVER HOLOGRAPHIC")
    #re.findall(rf"(.*)\s({'|'.join(finishes)}).*\s(\w+)?\s(\w+)?$", "RED GLITTER WITH A HINT OF SILVER HOLOGRAPHIC")
    #re.findall(rf"(.*)\s({'|'.join(finishes)}).*\s(\w+\s\w+)?$", "RED GLITTER WITH A HINT OF SILVER HOLOGRAPHIC"
    #re.findall(rf"^(.*)\s({'|'.join(finishes)}).*\s(\w+\s\w+)?$", "RED GLITTER WITH SILVER HOLOGRAPHIC")

    #re.findall(rf"^(.*?)\s({'|'.join(finishes)}).*?(\s\w+\s\w+)?$", "RED GLITTER WITH SILVER HOLOGRAPHIC")
    #re.findall(rf"^(.*?)\s({'|'.join(finishes)}).*?(\w+\s\w+)?$", "LIGHT PINK SHIMMER")

    #First remove string before 'oz.'
    #Example: "Morgan Taylor Not So Prince Charming Nail Lacquer, 0.5 oz. BLUE CR&Egrave;ME"
    #Can remove using re.sub: https://stackoverflow.com/questions/30945784/how-to-remove-all-characters-before-a-specific-character-in-python
    df['alt_text_new'] = df['alt_text'].apply(lambda text: re.sub(r'^.*?(?:oz.|Disco Days Nail Lacquer)', '', text))

    df['split'] = df['alt_text_new'].apply(lambda x: re.findall(rf"^(.*?)\s({'|'.join(finishes)}).*?(\w+\s\w+)?$", x))
    #Exceptions
    #DEEP PURPLE WITH SUBTLE PEARL
    #Morgan Taylor Disco Days Nail Lacquer GREEN HOLOGRAPHIC -fixed
    #MULTI DIMENSIONAL ORANGE METALLIC
    #Different orders
    #LIGHT TRANSLUCENT PINK
    #SHEER PINK WITH SILVER FROST
    #HOLOGRAPHIC PINK GLITTER
    #TODO: add ? to above expressions to account for optional secondary finishes
    return df

def get_df():
    json_file = "../../data/morgan_taylor_nail_lacquers.json"
    df = pd.read_json(json_file)
    #Parse alt_text for color shade, primary finish and secondary finish
    df = split_alt_text_into_desc(df)
    return df


if __name__ == '__main__':
    print(os.getcwd())
    #dir = "../data'
    #dir = "/Users/justinchassin/PycharmProjects/nailPolishProj"
    df = get_df()
    pass