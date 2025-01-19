import json
import time
from random import randint
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import re

class SallyHansenScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        url_to_scrape = 'https://www.sallyhansen.com/en-us/nail-color'
        self.driver.get(url_to_scrape)
        self.dismiss_cookies_window()

    def dismiss_cookies_window(self):
        WebDriverWait(self.driver, randint(5, 10)).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()


    def get_polish_names_from_page(self):
        html_doc = self.driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')
        polish_names = [heading.text.strip('\u200b') for heading in soup.find_all('h5', class_='heading cardo__heading')]
        return polish_names

    def click_view_more_buttons(self):
        # Click on 'View More' button in each section if it's available
        # https://stackoverflow.com/questions/46449200/xpath-for-a-span-based-on-its-text
        # view_more_buttons = [span.parent for span in soup.find_all('span', string='View More')]

        # https://stackoverflow.com/questions/46449200/xpath-for-a-span-based-on-its-text
        # span is within buttons
        # // means descendents or self
        view_more_btns = self.driver.find_elements(By.XPATH, '//span[contains(text(),"View More")]')
        if view_more_btns:
            for btn in view_more_btns:
                self.driver.implicitly_wait(randint(5, 10))
                ActionChains(self.driver).move_to_element(btn).click().perform()
        return


    def get_checkboxes(self):
        html_doc = self.driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')
        checkboxes = soup.find_all('input', class_='checkbox__input')
        return checkboxes

    def get_checkbox_ids_by_filter_category(self):
        checkboxes = self.get_checkboxes()
        checkbox_ids = [checkbox['id'] for checkbox in checkboxes]
        #using re to extract filter category (Nail Color, Finish, etc.)
        #Each checkbox id starts with 'filter-option-' and ends with '-{value}'
        #Get filter categories and all possible values. This can be used to reconstruct the id later on
        #https://stackoverflow.com/questions/6903557/splitting-on-first-occurrence
        #product_names_by_line = get_product_names_by_line(driver)
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

    def get_product_names_by_line(self):
        html_doc = self.driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')

        # iterate thru each variant filter results div to get:
        # Collection name: h3 element, class='heading filter-product-banner__title'
        # Collection description: h5 element, 'heading filter-product-banner__description'
        # Product link: link with data-test='cardo-element-link', get href
        # Product name: h5, class="heading cardo__heading"

        # Before parsing, click on all 'View More' buttons to expand produce sections
        self.click_view_more_buttons()

        product_names_and_links_by_line = []
        product_line_sections = soup.find_all('div', class_='variant-filter-results')
        for product_line in product_line_sections:
            collection_name = product_line.find_all('h3', class_='heading filter-product-banner__title')[0].text
            collection_description = product_line.find_all('h5', class_='heading filter-product-banner__description')[
                0].text
            product_line_res = {}
            product_line_res['collection_name'], product_line_res[
                'collection_desc'] = collection_name, collection_description
            product_line_res['polishes'] = []
            # the below element contains both product link and product names
            product_list = product_line.find_all('a', {
                'data-test': 'cardo-element-link'})  # easier to locate products by data-test field, since class name is long
            for prod in product_list:
                link = prod['href']
                name = prod.find_all('h5', 'heading cardo__heading')[0].text
                product_line_res['polishes'].extend([{'name': name, 'link': link}])
            product_names_and_links_by_line.append(product_line_res)

            self.driver.quit()

            # save to file
            output_dir = '../../../../data'
            output_file_name = "sally_hansen_products_and_links_by_line.json"
            output_path = os.path.join(output_dir, output_file_name)
            with open(output_path, 'w') as fp:
                json.dump(product_names_and_links_by_line, fp, indent=2)


    def get_products_by_filter_category(self):
        try:
            #Get checkbox filters
            checkbox_filters = self.get_checkbox_ids_by_filter_category()

            #Filter subset of checkbox filters
            #I changed the order of filters_to_keep to fix stale element issue:
            # https://stackoverflow.com/questions/27003423/staleelementreferenceexception-on-python-selenium
            # Previously, the browser would go back to 'https://www.sallyhansen.com/en-us/' after Wine/Burgundy/Berry checkbox was clicked
            #Research:
                #  https://stackoverflow.com/questions/18778320/how-can-i-find-the-code-thats-refreshing-the-page
                # Things in JS that may cause page to refresh:
                # (1) timers: setTimeout(), setInterval()
                # (2) broken selectors: may have clicked event handlers attached to whole document or Divs
                # (3) code that can redirect browser to different url
            # From Google: check out session management, redirect codes in html responses, user-agent detection, rate-limiting

            # I ended up making the request more random by changing the order of filters_to_keep.
            # Another idea was to split up this large request into smaller requests, in case rate-limiting was the problem.
            filters_to_keep = ['Product Line', 'Nail Color','Texture/Finish']
            checkbox_filters_to_keep = {k: checkbox_filters[k] for k in filters_to_keep}

            # I decided to make the key the product_name in the below dictionary, to make formatting in data_transform step easier
            # https://stackoverflow.com/questions/18837262/convert-python-dict-into-a-dataframe

            attributes_by_product = {}

            for filter_category in checkbox_filters_to_keep:
                for value in checkbox_filters_to_keep[filter_category]:
                    self.driver.implicitly_wait(randint(1, 5))
                    checkbox_id = f"filter-option-{filter_category}-{value}"
                    #wait until element is clickable wasn't working
                    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
                    checkbox = self.driver.find_element(By.ID, checkbox_id)
                    #checkbox = WebDriverWait(driver,  randint(1, 5), ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID,checkbox_id)))
                    #for each checkbox, click, collect and save polishes from page, and click again to reset filter

                    #Handling ElementClickInterceptedException(): element is not clickable at (x,y). Another element would receive the click
                    #This was bc element is not visible on the page. The previous steps land on the bottom of the website
                    #https://stackoverflow.com/questions/72460250/python-selenium-element-is-not-clickable-at-point-even-while-using-wait-until-el
                    #Before clicking, move to element on site
                    ActionChains(self.driver).move_to_element(checkbox).click().perform()
                    #Click on any View-More Buttons if they exist, to show hidden products
                    self.click_view_more_buttons()
                    self.driver.implicitly_wait(randint(1, 3))
                    #get polish names
                    polish_names_for_attribute = self.get_polish_names_from_page()
                    for polish in polish_names_for_attribute:
                        if polish not in attributes_by_product:
                            attributes_by_product[polish] = {}
                            attributes_by_product[polish][filter_category] = value
                        else:
                            attributes_by_product[polish][filter_category] = value
                    #products_by_filter_group[filter_category][value] = self.get_polish_names_from_page()
                    ActionChains(self.driver).move_to_element(checkbox).click().perform()
                    #unclick checkbox
                    self.driver.implicitly_wait(randint(1, 3))

            self.driver.quit()


            #save to file
            output_dir = '../../../../data'
            output_file_name = "sally_hansen_products_by_filter.json"
            output_path = os.path.join(output_dir, output_file_name)
            with open(output_path, 'w') as fp:
                json.dump(attributes_by_product, fp, indent=2)



            #Can get color_shades on ulta website
            #https://www.ulta.com/p/insta-dri-nail-polish-pimprod2042070?sku=2611172

            # open_filters_btn = WebDriverWait(driver, randint(5, 10)).until(
            # #     EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/div/div/div[1]/button')))
            # # open_filters_btn.click()
            # filter_checkbox = WebDriverWait(driver, randint(5, 10)).until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@id="filter-option-Nail Color-Green"]')))
            # filter_checkbox.click()
            #Collect all checkbox ids
           # checkbox_filters = get_checkbox_ids_by_filter_category(driver)
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



if __name__ == '__main__':
    SallyHansenScraper().get_products_by_filter_category()
    #SallyHansenScraper().get_product_names_by_line()


