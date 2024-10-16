import json
import time
from random import randint
import os
import requests
import webcolors

from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np




def get_each_lacquer_product(driver, color):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    # For each color, get alt-texts for all polish images
    # alt-texts are in img elements class "contain svelte-9x92ar"
    # Format: "Morgan Taylor {product_name} Nail Lacquer, 0.5 oz. {polish_description} {Creme}"
    # In above format, {product name} may be after 'Nail Lacquer" and {Creme} may not appear
    # Get hrefs (can use later on to refine descriptions)
    #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-name-argument
    product_cards = soup.find_all('div', class_="card-container swatch svelte-1cmn0v2")
    polish_list = []
    for product in product_cards:
        #https://stackoverflow.com/questions/56532991/with-beautifulsoup-how-do-i-search-for-an-element-class-wtihin-a-class
        link = product.find_all('a', class_="image svelte-1cmn0v2")[0]['href']
        product_name = product.find_all('p')[0].text
        #get description at the end of alt-text
        alt_text = product.find_all('img')[0]['alt']
        #.partition('0.5 oz.')[-1]
        polish_list.append({'product_name': product_name, 'color': color, 'alt_text': alt_text, 'link': link})

    return polish_list


def get_each_vegan_polish_link(driver):
    #Collect links to each product
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    list_of_products = soup.find_all('a', class_='information svelte-1burahp')
    product_links = [prod['href'] for prod in list_of_products]
    return product_links

def parse_vegan_polish_link(driver):
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, 'html.parser')
    #Note: find gets the first match, while find_all gets all matches (https://stackoverflow.com/questions/59780916/what-is-the-difference-between-find-and-find-all-in-beautiful-soup-python)
    name = soup.find('h2', class_='svelte-apy8jy')
    #Description is in the first paragraph element
    description = soup.find('div', class_='text product-description svelte-apy8jy').find('p')
    top_colors_by_percent = None

    if name is not None:
        name = name.text
    if description is not None:
        description = description.text

    #save screenshot of image using pillow library. This will be used in data_transform to determine color_family
    #the below image is a swatch picture of the color, which is easier to get color_family from than noisier picture of bottle
    polish_img = soup.find_all('img', class_='contain svelte-9x92ar')[1]
    img_src_url = polish_img['src']

    #https://pillow.readthedocs.io/en/stable/reference/Image.html
    #https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image
    #https://www.tutorialspoint.com/how-to-open-an-image-from-the-url-in-pil
    #Using requests library to send GET request for image url, and retrieve the raw Response object content
    #stream=True prevents immediate memory storage
    try:
        #https://stackoverflow.com/questions/57539233/how-to-open-an-image-from-an-url-with-opencv-using-requests-from-python
        response = requests.get(img_src_url, stream=True).raw
        with Image.open(response) as img:


            #Crop a small section in the center of image using Image.crop:
            #https://pillow.readthedocs.io/en/stable/_modules/PIL/Image.html#Image.crop
            #This will reduce the # of colors to look at and account for glitter polishes
            #that have particles of multiple colors
            #Non-glitter and non-metallic polishes should only have 1 color value in the region
            (left, upper, right, lower) = (55, 55, 65, 65)
            img = img.crop((left, upper, right, lower))

            #https://stackoverflow.com/questions/59507676/how-to-get-the-dominant-colors-using-pillow
            reduced = img.convert("P", palette=Image.WEB)
            image_dimensions = reduced.size
            length = image_dimensions[0]
            width = image_dimensions[1]
            total_pixels = length * width
            center_x = length / 2
            center_y = width / 2
            crop_radius = 10  # number of pixels from center

            palette = reduced.getpalette()
            palette = [palette[3*n:3*n+3] for n in range(256)]
            color_concentrations = [(n, palette[m]) for n,m in reduced.getcolors()]
            #take top 3 color_concentrations
            #convert to percent out of total pixels
            #If a color makes up a large enough percent threshold, it will represent the primary color
            #Ignoring black background [RGB value = (255,255,255)]
            #TODO: improve process by cropping out background color
            color_concentrations.sort(reverse=True)
            colors_by_percent = [(num_of_color / total_pixels, rgb_value) for num_of_color, rgb_value in
                                 color_concentrations]
            #Take top 3 color concentrations in cropped region
            #top_colors_by_percent = colors_by_percent[0:3] if len(colors_by_percent)>=3 else
            #https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green-with-python
        #https://www.quora.com/Can-we-accept-an-image-URL-as-input-in-Python
        #img = np.asarray(bytearray(response.read()), dtype="uint8")
        #rgb_image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        #https://stackoverflow.com/questions/21596281/how-does-one-convert-a-grayscale-image-to-rgb-in-opencv-python
        #https://docs.opencv.org/4.x/d3/df2/tutorial_py_basic_ops.html
        #https://stackoverflow.com/questions/63081974/converting-rgb-to-hex
        # #From OpenCV docs, for imdecode(), color images are stored in BGR order
        # image = cv2.imdecode(img, cv2.IMREAD_COLOR)
        # #cv2.imshow('image', image)
        pass

    except Exception as e:
        print(e)
        return '', '', ''

    return name, description, colors_by_percent

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
    # url_to_scrape = 'https://gelish.com/colors/morgan-taylor'
    # driver.get(url_to_scrape)

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

        driver.quit()

        output_dir = '../data'
        output_file_name = "morgan_taylor_nail_lacquers.json"
        output_path = os.path.join(output_dir, output_file_name)
        with open(output_path, 'w') as fp:
            json.dump(nail_lacquers, fp, indent=2)
        driver.close()

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
        # driver.quit()
    except Exception as e:
        print(e)
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
            driver.implicitly_wait(randint(1, 3))
            driver.get(url_to_scrape)
            dismiss_cookies_window(driver)
            name, description, top_colors_by_percent = parse_vegan_polish_link(driver)
            polish = {'product_name': name, 'top_colors_by_percent': top_colors_by_percent, 'description': description, 'link': url_to_scrape}
            polishes.append(polish)

        #driver.quit()

        # output_dir = '../../data'
        # output_file_name = "morgan_taylor_vegan_polishes.json"
        # output_path = os.path.join(output_dir, output_file_name)
        with open("morgan_taylor_vegan_polishes.json", 'w') as fp:
            json.dump(polishes, fp, indent=1)
        #driver.close()


    except Exception as e:
        print(e)
        #driver.quit()
        #driver.close()

    finally:
        driver.quit()


if __name__ == '__main__':
   #get_lacquer_products()
    get_vegan_polishes()