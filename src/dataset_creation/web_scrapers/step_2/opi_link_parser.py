from random import randint
import requests
import os
import concurrent.futures

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import cv2
import pandas as pd
import datetime

import numpy as np
from src.dataset_creation.data_transform.tools.image_color_classification.image_color_classification import get_dominant_color_in_np_image

def dismiss_cookies_window(driver):
    # Dimiss cookies pop up
    # https://stackoverflow.com/questions/46669850/using-aria-label-to-locate-and-click-an-element-with-python3-and-selenium
    # I chose to use aria-label bc it was simpler to find elements
    # No-thanks button: aria-label="Reject All"
    # "yes-thanks button: aria-label: "Allow All"
    try:
        WebDriverWait(driver, randint(10, 15)).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()
    except TimeoutException:
        #if button does not exist, skip
        return

def parse_lacquer_link(driver, link):
    driver.implicitly_wait(randint(1, 3))
    root = "https://opi.com"
    link = root + link
    driver.get(link)
    dismiss_cookies_window(driver)
    #wait for all the images to load
    driver.implicitly_wait(randint(1, 3))
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    #Note: find gets the first match, while find_all gets all matches (https://stackoverflow.com/questions/59780916/what-is-the-difference-between-find-and-find-all-in-beautiful-soup-python)
    try:
        #Use XPath contains method to find swatch images
        #Get 3rd picture from list of images
        swatch_img_tag = driver.find_elements(By.XPATH, "//img[contains(@srcset, '16w')]")[2]
        img_url = swatch_img_tag.get_attribute("srcset").split(",")[-1].split(" ")[1] #TODO: clean up line
        response = requests.get(img_url, stream=True).raw
        img = np.asarray(bytearray(response.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        dominant_rgb_color = get_dominant_color_in_np_image(img)
        #https://stackoverflow.com/questions/30167538/convert-a-numpy-ndarray-to-stringor-bytes-and-convert-it-back-to-numpy-ndarray
        dominant_rgb_color = ','.join(str(val) for val in dominant_rgb_color)

    except Exception as e:
        print(f"Issue parsing {link}: {e}")
        return '', ''

    return dominant_rgb_color, str(datetime.datetime.now())

def scrape_link_data_from_batch(batch: pd.DataFrame) -> pd.DataFrame:
    driver = webdriver.Chrome()
    try:
        batch['dominant_rgb_color'], batch['time_collected'] = zip(
        *batch['href'].apply(lambda x: parse_lacquer_link(driver, x)))
    except Exception as e:
        print(e)
    finally:
        driver.quit()
        return batch


def scrape_link_data():
    try:
        #get input data from step 1
        data = pd.read_json("../../../../data/step_1/opi_products_pages_1_thru_last_page.json")

        #Use multithreading to speed up link parsing (for ~500 products)
        available_processors = os.cpu_count()
        batches = np.array_split(data, available_processors)

        with concurrent.futures.ProcessPoolExecutor(available_processors) as executer:
            output = pd.concat(executer.map(scrape_link_data_from_batch, batches))

        output_dir = '../../../../data/step_2'
        output_file_name = "opi_products.parquet"
        output_path = output_dir + "/" + output_file_name
        output.to_parquet(output_path)

    except Exception as e:
        print(e)

if __name__=='__main__':
    scrape_link_data()


