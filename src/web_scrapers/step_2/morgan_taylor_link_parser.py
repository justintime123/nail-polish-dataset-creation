import json
from random import randint
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import cv2
import pandas as pd
import datetime
from src.utils.path import Path

import numpy as np
from src.data_transform.image_color_classification import get_dominant_color_in_np_image

def dismiss_cookies_window(driver):
    # Dimiss cookies pop up
    # https://stackoverflow.com/questions/46669850/using-aria-label-to-locate-and-click-an-element-with-python3-and-selenium
    # I chose to use aria-label bc it was simpler to find elements
    # No-thanks button: aria-label="Reject All"
    # "yes-thanks button: aria-label: "Allow All"
    try:
        cookies_btn = WebDriverWait(driver, randint(5, 10)).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Reject All"]')))
        cookies_btn.click()
    except TimeoutException:
        #if button does not exist, skip
        return

def parse_lacquer_link(driver, link):
    driver.implicitly_wait(randint(1, 3))
    root = "https://gelish.com"
    link = root + link
    driver.get(link)
    dismiss_cookies_window(driver)
    #wait for all the images to load
    driver.implicitly_wait(randint(1, 3))
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    #Note: find gets the first match, while find_all gets all matches (https://stackoverflow.com/questions/59780916/what-is-the-difference-between-find-and-find-all-in-beautiful-soup-python)
    try:
        name = soup.find('h2', class_='svelte-1ml6a2w')
        # Description is in the first paragraph element
        description = soup.find('div', class_='text product-description svelte-1ml6a2w').find('p')

        if name is not None:
            name = name.text.strip().upper()
        if description is not None:
            description = description.text.upper()

        # save screenshot of image using pillow library. This will be used in data_transform to determine color_family
        # the below image is a swatch picture of the color, which is easier to get color_family from than noisier picture of bottle
        images = soup.find_all('img', class_='contain svelte-9x92ar')
        swatch_img = [tag for tag in images if
                      (name in tag['alt'].upper() or description in tag['alt'].upper()) and 'SWATCH' in tag[
                          'src'].upper()]
        img_src_url = swatch_img[0]['src']
        response = requests.get(img_src_url, stream=True).raw

        img = np.asarray(bytearray(response.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        dominant_rgb_color = get_dominant_color_in_np_image(img)
        #https://stackoverflow.com/questions/30167538/convert-a-numpy-ndarray-to-stringor-bytes-and-convert-it-back-to-numpy-ndarray
        dominant_rgb_color = ','.join(str(val) for val in dominant_rgb_color)

    except Exception as e:
        print(f"Issue parsing {name} at url {link}:")
        print(e)
        return '', '', ''

    return dominant_rgb_color, str(datetime.datetime.now())

def parse_vegan_polish_link(driver, link):
    driver.implicitly_wait(randint(1, 3))
    driver.get(link)
    dismiss_cookies_window(driver)
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    #Note: find gets the first match, while find_all gets all matches (https://stackoverflow.com/questions/59780916/what-is-the-difference-between-find-and-find-all-in-beautiful-soup-python)
    name = soup.find('h2', class_='svelte-1ml6a2w')
    #Description is in the first paragraph element
    description = soup.find('div', class_='text product-description svelte-1ml6a2w').find('p')

    if name is not None:
        name = name.text
    if description is not None:
        description = description.text

    #save screenshot of image using pillow library. This will be used in data_transform to determine color_family
    #the below image is a swatch picture of the color, which is easier to get color_family from than noisier picture of bottle
    polish_img = soup.find_all('img', class_='contain svelte-9x92ar')[-1]
    img_src_url = polish_img['src']
    #https://pillow.readthedocs.io/en/stable/reference/Image.html
    #https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image
    #https://www.tutorialspoint.com/how-to-open-an-image-from-the-url-in-pil
    #Using requests library to send GET request for image url, and retrieve the raw Response object content
    #stream=True prevents immediate memory storage
    #TODO: convert image from grayscale to rgb color
    try:
        #https://stackoverflow.com/questions/57539233/how-to-open-an-image-from-an-url-with-opencv-using-requests-from-python
        response = requests.get(img_src_url, stream=True).raw

        img = np.asarray(bytearray(response.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        dominant_rgb_color = get_dominant_color_in_np_image(img)
        #https://stackoverflow.com/questions/30167538/convert-a-numpy-ndarray-to-stringor-bytes-and-convert-it-back-to-numpy-ndarray
        dominant_rgb_color = ','.join(str(val) for val in dominant_rgb_color)

    except Exception as e:
        print(e)
        return '', '', ''

    return name, dominant_rgb_color, description, str(datetime.datetime.now())

def scrape_data_from_each_vegan_product_link():
    try:
        driver = webdriver.Chrome()
        #get input data from step 1
        data = pd.read_json("../../../data/step_1/morgan_taylor_vegan_polishes.json")
        #iterate thru each link and append new data

        #https://stackoverflow.com/questions/23586510/return-multiple-columns-from-pandas-apply
        data['product_name'], data['dominant_rgb_color'], data['description'], data['time_collected'] = zip(*data['link'].apply(lambda x: parse_vegan_polish_link(driver, x)))

        output_dir = '../../../data/step_2'
        output_file_name = "morgan_taylor_vegan_polishes.parquet"
        output_path = output_dir + "/" + output_file_name
        data.to_parquet(output_path)

    except Exception as e:
        print(e)
        #driver.quit()
        #driver.close()

    finally:
        driver.quit()

def scrape_data_from_each_lacquer_link():
    try:
        driver = webdriver.Chrome()
        #get input data from step 1
        data = pd.read_json("../../../data/step_1/morgan_taylor_nail_lacquers.json")
        #iterate thru each link and append new data

        #https://stackoverflow.com/questions/23586510/return-multiple-columns-from-pandas-apply
        data['dominant_rgb_color'], data['time_collected'] = zip(*data['link'].apply(lambda x: parse_lacquer_link(driver, x)))

        output_dir = '../../../data/step_2'
        output_file_name = "morgan_taylor_lacquer_polishes.parquet"
        output_path = output_dir + "/" + output_file_name
        data.to_parquet(output_path)

    except Exception as e:
        print(e)
        #driver.quit()
        #driver.close()

    finally:
        driver.quit()


if __name__=='__main__':
    #scrape_data_from_each_vegan_product_link()
    scrape_data_from_each_lacquer_link()


