import json
from random import randint
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait




def get_each_lacquer_product(driver, color):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    # For each color, get alt-texts for all polish images
    # alt-texts are in img elements class "contain svelte-9x92ar"
    # Format: "Morgan Taylor {product_name} Nail Lacquer, 0.5 oz. {polish_description} {Creme}"
    # In above format, {product name} may be after 'Nail Lacquer" and {Creme} may not appear
    # Get hrefs (can use later on to refine descriptions)
    #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-name-argument
    product_cards = soup.find_all('div', class_="card-container swatch svelte-1m5vxtt")
    if len(product_cards)==0:
        print("Issue retrieving products - check class ids in HTML")
    polish_list = []
    for product in product_cards:
        #https://stackoverflow.com/questions/56532991/with-beautifulsoup-how-do-i-search-for-an-element-class-wtihin-a-class
        link = product.find_all('a', class_="image svelte-1m5vxtt")[0]['href']
        product_name = product.find_all('p')[0].text
        #get description at the end of alt-text
        alt_text = product.find_all('img')[0]['alt']
        #.partition('0.5 oz.')[-1]
        polish_list.append({'product_name': product_name, 'color': color, 'alt_text': alt_text, 'link': link, 'time_collected': str(datetime.datetime.now())})

    return polish_list


def get_each_vegan_polish_link(driver):
    #Collect links to each product
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    list_of_products = soup.find_all('a', class_='information svelte-1m5vxtt')
    product_links = [prod['href'] for prod in list_of_products]
    return product_links


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


def get_lacquer_products():

    try:
        driver = webdriver.Chrome()
        nail_lacquers = []

        base_url = 'https://gelish.com/colors/morgan-taylor'
        # hard-coding the colors for now, instead of using Selenium to scroll thru input element
        color_list = ['purple', 'pink', 'red', 'orange-coral', 'yellow', 'green-blue', 'neutral', 'metallic', 'glitter']
        for color in color_list:
            url_to_scrape = base_url + '/' + color
            try:
                driver.get(url_to_scrape)
                dismiss_cookies_window(driver)
                parsed_polishes = get_each_lacquer_product(driver, color)
                nail_lacquers.extend(parsed_polishes)
            except Exception as e:
                print(e)

        output_dir = '../data/step_1'
        output_file_name = "morgan_taylor_nail_lacquers.json"
        output_path = output_dir + "/" + output_file_name
        with open(output_path, 'w') as fp:
            json.dump(nail_lacquers, fp, indent=2)
        driver.close()
    except Exception as e:
        print(e)
        driver.quit()
    finally:
        driver.quit()

def get_vegan_polishes():
    try:
        driver = webdriver.Chrome()
        url = 'https://gelish.com/morgan-taylor/naturals'
        driver.get(url)
        dismiss_cookies_window(driver)
        #each link contains polish description
        links = get_each_vegan_polish_link(driver)
        polishes = []

        base_url = 'https://gelish.com'
        for link in links:
            url_to_scrape = base_url + '/' + link
            polish = {'link': url_to_scrape, 'time_collected': str(datetime.datetime.now())}
            polishes.append(polish)

        output_dir = '../data/step_1'
        output_file_name = "morgan_taylor_vegan_polishes.json"
        output_path = output_dir + "/" + output_file_name
        with open(output_path, 'w') as fp:
            json.dump(polishes, fp, indent=1)

    except Exception as e:
        print(e)
    finally:
        driver.quit()


if __name__ == '__main__':
   get_lacquer_products()
   #get_vegan_polishes()