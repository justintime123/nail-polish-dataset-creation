import json
import time
from random import randint
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import re

def get_colors_by_product_name():
    return None

def get_finishes_by_product_name():
    return None

def get_product_names_by_line(driver):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')

    # iterate thru each variant filter results div to get:
    # Collection name: h3 element, class='heading filter-product-banner__title'
    # Collection description: h5 element, 'heading filter-product-banner__description'
    # Product link: link with data-test='cardo-element-link', get href
    # Product name: h5, class="heading cardo__heading"
    # Click on 'View More' button in each section if it's available

    product_names_and_links_by_line = []
    #TODO: click thru "View More" buttons in each section before parsing products

    product_line_sections = soup.find_all('div', class_='variant-filter-results')
    for product_line in product_line_sections:
        collection_name = product_line.find_all('h3', class_='heading filter-product-banner__title')[0].text
        collection_description = product_line.find_all('h5', class_='heading filter-product-banner__description')[0].text
        product_line_res = {}
        product_line_res['collection_name'], product_line_res['collection_desc'] = collection_name, collection_description
        product_line_res['polishes'] = []
        #the below element contains both product link and product names
        product_list = product_line.find_all('a', {'data-test': 'cardo-element-link'}) #easier to locate products by data-test field, since class name is long
        for prod in product_list:
            link = prod['href']
            name = prod.find_all('h5', 'heading cardo__heading')[0].text
            product_line_res['polishes'].extend([{'name': name, 'link': link}])
        product_names_and_links_by_line.append(product_line_res)

    return product_names_and_links_by_line

def get_checkboxes(driver):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    checkboxes = soup.find_all('input', class_='checkbox__input')
    return checkboxes

def get_checkbox_ids_by_filter_category(driver):
    checkboxes = get_checkboxes(driver)
    checkbox_ids = [checkbox['id'] for checkbox in checkboxes]
    #using re to extract filter category (Nail Color, Finish, etc.)
    #Each checkbox id starts with 'filter-option-' and ends with '-{value}'
    #Get filter categories and all possible values. This can be used to reconstruct the id later on
    #https://stackoverflow.com/questions/6903557/splitting-on-first-occurrence
    product_names_by_line = get_product_names_by_line(driver)
    filter_categories_and_values = [s.replace('filter-option-', '').split('-', 1) for s in checkbox_ids]
    filter_values_by_category = {}
    for l in filter_categories_and_values:
        filter_name = l[0]
        filter_values = l[1:]
        if l[0] in filter_values_by_category.keys():
            filter_values_by_category[filter_name].extend(filter_values)
        else:
            filter_values_by_category[filter_name] = filter_values
    return filter_values_by_category

if __name__ == '__main__':
    # url_to_scrape = 'https://gelish.com/colors/morgan-taylor'
    # driver.get(url_to_scrape)

    try:
        driver = webdriver.Chrome()
        url_to_scrape = 'https://www.sallyhansen.com/en-us/nail-color'
        driver.get(url_to_scrape)
        #Dismiss cookies window
        WebDriverWait(driver, randint(5, 10)).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()
        time.sleep(randint(1, 5))

        products_by_product_line = get_product_names_by_line(driver)

        checkbox_filters = get_checkbox_ids_by_filter_category(driver)
        for filter_category in checkbox_filters:
            for value in filter_category:
                checkbox_id = f"filter-option-{filter_category}-{value}"
                #wait until element is clickable wasn't working
                checkbox = driver.find_element('id', checkbox_id)
                checkbox.click()
                #get polish names and product line
                #unclick checkbox

        #Can get color_shades on ulta website
        #https://www.ulta.com/p/insta-dri-nail-polish-pimprod2042070?sku=2611172

        # open_filters_btn = WebDriverWait(driver, randint(5, 10)).until(
        #     EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/div/div/div[1]/button')))
        # open_filters_btn.click()
        filter_checkbox = WebDriverWait(driver, randint(5, 10)).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="filter-option-Nail Color-Green"]')))
        filter_checkbox.click()
        #Collect all checkbox ids
        checkbox_filters = get_checkbox_ids_by_filter_category(driver)
        #while there are available colors
        #Select checkbox, get all product names, and deselect checkbox
        #https://stackoverflow.com/questions/21213417/select-checkbox-using-selenium-with-python
        # filter_checkbox = WebDriverWait(driver, randint(5, 10)).until(
        # EC.element_to_be_clickable((By.XPATH, '//*[@id="filter-option-Nail Color-Green"]')))
        # filter_checkbox = WebDriverWait(driver, randint(5,10)).until(
        #     EC.element_to_be_clickable((By.XPATH, '//*[@id="filter-option-Nail Color-Green"]')))
        pass
    except Exception as e:
        print(e)

