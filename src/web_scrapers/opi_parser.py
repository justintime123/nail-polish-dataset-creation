import json
import time
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# For all prods in polish_list, get below attrs and parse for Product Type/Product Name
# I excluded data-color-family-secondary, data-color-depth, and data-color-hex bc most of these were null
attrs_to_parse = ['data-color-family-primary',
                  'data-color-subgroup',
                  'data-color-finish',
                  'data-color-system',
                  'href'  # will use hrefs to later parse descriptions for each product, opi.com/products/href[-1]
                  ]


def get_each_by_opi_product_tag(driver):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    polish_list = soup.find_all("a", "productCard__titles")  # find_all also gets descendents
    return polish_list


def get_attrs_for_product(prod_dict):
    return dict((k, prod_dict[k]) for k in attrs_to_parse)


def get_product_type_and_name(prod_tag):
    # getting Product Type and Product names, using contents
    # https://stackoverflow.com/questions/25251841/bs4-getting-text-in-tag
    return {'product-type': prod_tag.contents[0].text,
            'product-name': prod_tag.contents[1].text}



def get_attrs_by_product(driver):
    product_tags = get_each_by_opi_product_tag(driver)
    attrs_by_prod = [get_attrs_for_product(prod.attrs) | get_product_type_and_name(prod) for prod in product_tags]
    return attrs_by_prod



def click_show_more_btn(driver, url_has_page_number=False):
    time.sleep(randint(15, 20))
    # if url_has_page_number, there will be two load buttons and the xpath is different
    xpath = ' //*[@id="main"]/div[4]/section/div[3]/button' if url_has_page_number else '//*[@id="main"]/div[4]/section/div[2]/button'
    WebDriverWait(driver, randint(15, 20)).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def get_products_from_site(start_page=1, end_page=None):
    driver = webdriver.Chrome()
    url_to_scrape = ''
    url_has_page_number = False

    if start_page > 1:
        url_to_scrape = f"https://www.opi.com/collections/shop-products?page={start_page}&product-type=Nail%20Lacquer--Infinite%20Shine--Natural%20Origin%20Nail%20Lacquer"
        url_has_page_number = True
    else:
        url_to_scrape = "https://www.opi.com/collections/shop-products?product-type=Nail%20Lacquer--Infinite%20Shine--Natural%20Origin%20Nail%20Lacquer"
    driver.get(url_to_scrape)

    try:
        # Dismiss cookies pop-up
        # https://stackoverflow.com/questions/64032271/handling-accept-cookies-popup-with-selenium-in-python
        # https://stackoverflow.com/questions/59130200/selenium-wait-until-element-is-present-visible-and-interactable
        # https://stackoverflow.com/questions/43868009/how-to-resolve-elementnotinteractableexception-element-is-not-visible-in-seleni
        # Div id: onetrust-button-group
        # button id: onetrust-reject-all-handler
        # onetrust-accept-btn-handler
        WebDriverWait(driver, randint(10, 15)).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()

        # if end_page is None, click thru until the last page
        if end_page is None:
            while True:
                try:
                    click_show_more_btn(driver, url_has_page_number)
                except TimeoutException:
                    break

        else:
            num_clicks = end_page - start_page
            # Click show-more button
            for i in range(num_clicks):
                click_show_more_btn(driver, url_has_page_number)

        # Get product results
        time.sleep(randint(30, 40))
        prods = get_attrs_by_product(driver)
        # Write results to json file
        end_page = 25
        output_file = f"data/opi_products_pages_{start_page}_thru_{end_page}.json"
        with open(output_file, 'w') as fp:
            json.dump(prods, fp)
        driver.close()

    except Exception as e:
        print(e)
        driver.quit()


if __name__ == '__main__':
    get_products_from_site(start_page=1)
    # get_products_from_site(start_page=1, end_page=5)
    # get_products_from_site(start_page=6, end_page=10)
    # get_products_from_site(start_page=11, end_page=15)
    # get_products_from_site(start_page=16, end_page=20)
