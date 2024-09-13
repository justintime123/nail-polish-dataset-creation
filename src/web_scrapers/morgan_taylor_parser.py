import json
import time
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

def parse_alt_text(text):
    #Get finish_type and description from alt_text
    return


def get_each_lacquer_product(driver):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    # For each color, get alt-texts for all polish images
    # alt-texts are in img elements class "contain svelte-9x92ar"
    # Format: "Morgan Taylor {product_name} Nail Lacquer, 0.5 oz, {polish_description} {Creme}"
    # In above format, {product name} may be after 'Nail Lacquer" and {Creme} may not appear
    # Get hrefs (can use later on to refine descriptions)
    #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-name-argument
    product_cards = soup.find_all('div', class_="card-container swatch svelte-1cmn0v2")
    polish_list = {}
    for product in product_cards:
        #https://stackoverflow.com/questions/56532991/with-beautifulsoup-how-do-i-search-for-an-element-class-wtihin-a-class
        link = product.find_all('a', class_="image svelte-1cmn0v2")[0]['href']
        product_name = product.find_all('p')[0].text
        alt_text = product.find_all('img')[0]['alt'] #TODO: Modify to exclude text before 0.5 oz
        polish_list[product_name] = [alt_text, link]

    return polish_list

def get_each_vegan_polish_link(driver):
    #Collect links to each product
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')

def dismiss_cookies_window(driver):
    # Dimiss cookies pop up
    # https://stackoverflow.com/questions/46669850/using-aria-label-to-locate-and-click-an-element-with-python3-and-selenium
    # I chose to use aria-label bc it was simpler to find elements
    # No-thanks button: aria-label="No, thanks."
    # "yes-thanks button: aria-label: "It´s Okay."
    WebDriverWait(driver, randint(10, 15)).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="No, thanks."]'))).click()

    time.sleep(randint(15, 20))


if __name__ == '__main__':
    # url_to_scrape = 'https://gelish.com/colors/morgan-taylor'
    # driver.get(url_to_scrape)

    try:
        driver = webdriver.Chrome()
        nail_lacquers = {}
        vegan_polishes = {}

        base_url = 'https://gelish.com/colors/morgan-taylor'
        # hard-coding the colors for now, instead of using Selenium to scroll thru input element
        color_list = ['purple', 'pink', 'red', 'orange-coral', 'yellow', 'green-blue', 'neutral', 'metallic', 'glitter']
        for color in color_list:
            url_to_scrape = base_url + '/' + color
            driver.get(url_to_scrape)
            dismiss_cookies_window(driver)
            nail_lacquers[color] = get_each_lacquer_product(driver)
            driver.quit()

        # #Goal: keep sliding until color changes
        # #For each color category, thumb-bg changes and color label (
        # #thumb-bg changes color
        # #For each color change, save the color_name and parse all polishes under the color category
        #
        # slider = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[1]/div/div/div[3]/div[2]/input')
        # move = ActionChains(driver)
        # #Move slider to the left to start
        # #For each offset movement, check if color changed
        # #If so, store color and polished
        # #Otherwise keep going
        # move.click_and_hold(slider).move_by_offset(10, 0).release().perform()
        # time.sleep(15)
        #driver.quit()
    except Exception as e:
        print(e)
        driver.quit()