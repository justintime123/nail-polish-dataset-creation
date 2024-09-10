#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load
get_ipython().system(' pip3 install selenium')
get_ipython().system(' pip3 install requests')
get_ipython().system(' pip3 install pandas')
get_ipython().system(' pip3 install bs4')

import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from bs4 import BeautifulSoup
import requests
import time


get_ipython().system('python --version')
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By



# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[ ]:


#HTML
#List of products is in product-collection-list_products class 
#In each product (product-list-item_title), need the product name and description
#Description is found in link and product name is in span

#Scraping URL to understand how to get info for one nail polish
#https://www.essie.com/nail-polish/enamel/yellows

#https://www.geeksforgeeks.org/beautifulsoup-scraping-link-from-html/
#https://stackoverflow.com/questions/56455255/beautifulsoup-find-all-returns-nothing

def getHTMLDocument(url):
    response = requests.get(url)
    return response.text

def get_links_by_product(url_to_scrape, html_class_to_look_for, web_driver=None): 
    html_doc = web_driver.page_source if web_driver else getHTMLDocument(url_to_scrape)
    #print(html_doc)
    soup = BeautifulSoup(html_doc, 'html.parser')
    polish_list = soup.find_all("a", html_class_to_look_for)
    #print(polish_list)
    
    html_base = 'https://www.essie.com'

    links_by_product = {}
    for i in range(len(polish_list)):
        name = polish_list[i].span.text
        relative_link = polish_list[i].get("href")
        link = html_base + relative_link #adjusting HTML path to make it absolute
        links_by_product[name] = link #this assumes all nail polish names are unique
    return links_by_product



url_to_scrape = 'https://www.essie.com/nail-polish/enamel/yellows'
html_class_to_look_for = "product-list-item__title"
links_by_product = get_links_by_product(url_to_scrape, html_class_to_look_for)
links_by_product

#Rewriting using list comprehension
###links_by_product = [polish.name:base.append(polish.link) for polish in yellow_polishes]
# links_by_product = {yellow_polishes[item].span.text: yellow_polishes[item].get("href")
#                    for item in yellow_polishes}
#yellow_polishes[0].span.text
#yellow_polishes[0].get("href")


# In[ ]:


#Brainstorm of fields to collect for each polish

#Description
#Tags: color,finish and formula_type (eg, longwear, quick-dry, enamel). Some products might have multiple formula types (e.g., blanc is available in enamel or gel)
#Is the product discontinued?
#Reviews 
#Best-seller?

#Goal: Collect standardized data of nail polish colors across companies, so that they can be compared.


# In[ ]:


#Writing generic function
def get_tags_for_product(product_url):
    #Calls find_all function in Beautiful Soup
    html_doc = getHTMLDocument(product_url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    matching_elements = soup.find_all("li", "product-detail-info__tag")
    #matching_elements = soup.find_all("a", "tag__link")
    list_of_tags = [tag.text.replace('\n', '') for tag in matching_elements]
    return list_of_tags
    

#Getting tags for each polish
#Each tag is in li of product-detail-info__tag class
polish_descriptions = {}
for polish_name,link in links_by_product.items():
    tags = get_tags_for_product(link)
    polish_descriptions[polish_name] = tags


# In[ ]:


polish_descriptions


# In above, 'light and fairy' has color_family last and polish_type first

# In[ ]:


#Figuring out how to parse all elements in "select color family". 


# In[ ]:


#polish_descriptions['born to adorn'][0].get("cta_name")


# #Potential research questions (extensions)
# #How do the best-sellers change with each season?
# #How does the distribution of available colors differ between companies like Essie, OPI and Orly?
# #Are there certain color categories or attributes that predict discontinuation or have historically been discontinued?
# #For the above question, are there similar predictors for best-sellers?
# #The above questions can be combined in different ways
# 
# #Things to figure out
# #Breaking down color categories into sub-categories
# #How to handle undertones 
# 

# In[ ]:


#To get all of the polishes in one go, I decided to parse from the "shop-all section" ().
#The tags for each product might not come in order (like 'light and fairy' above), so I'll collect all possible filters first, so I can reorder the sets appropriately.

def getHTMLDocument(url):
    response = requests.get(url)
    return response.text

url_to_scrape = "https://www.essie.com/shop-all"
get_links_by_product(url_to_scrape, "product-grid-item__name") #have to adapt to use Selenium. Inspect shows final DOM, but BS is parsing HTML downloaded from server.
#The products in shop-all are dynamically generated using JS.





# In[ ]:


# !apt-get update # to update ubuntu to correctly run apt install
# !apt install -y chromium-chromedriver
# !cp /usr/lib/chromium-browser/chromedriver /usr/bin
import os
os.getcwd()


# In[ ]:


#!pip3 install chromedriver
#cService = Service(executable_path='/chromedriver/chromedriver.exe')
#options = webdriver.ChromeOptions()
import time
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://www.essie.com/shop-all')
#time.sleep(10)

def get_links_by_product_v2(url_to_scrape, html_class_to_look_for, web_driver=None): 
    html_doc = web_driver.page_source if web_driver else getHTMLDocument(url_to_scrape)
    #print(html_doc)
    soup = BeautifulSoup(html_doc, 'html.parser')
    polish_list = soup.find_all("a", html_class_to_look_for)
    #print(polish_list)
    
    html_base = 'https://www.essie.com'

    links_by_product = {}
    for i in range(len(polish_list)):
        name = polish_list[i].text.strip().replace('\n', '')
        relative_link = polish_list[i].get("href")
        link = html_base + relative_link #adjusting HTML path to make it absolute
        links_by_product[name] = link #this assumes all nail polish names are unique
    return links_by_product



page_1 = get_links_by_product_v2(url_to_scrape='https://www.essie.com/shop-all', html_class_to_look_for="product-grid-item__name", web_driver=driver) #have to adapt to use Selenium. Inspect shows final DOM, but BS is parsing HTML downloaded from server.

#https://stackoverflow.com/questions/36244877/python-selenium-clicking-next-button-until-the-end
#Using Selenium to click on 'Next Page'
#https://stackoverflow.com/questions/46669850/using-aria-label-to-locate-and-click-an-element-with-python3-and-selenium

next_btn = driver.find_element(By.CSS_SELECTOR, "[aria-label='Next Page']")
next_btn.click()


# In[ ]:


page_1


# In[ ]:


#Extending above function to collect rest of the colors
get_ipython().system('python --version')


# In[ ]:


#OPI brainstorm 
#Product types: Nail Lacquer, Infinite Shine, Gel, Vegan (Natural Origin Nail Lacquer)
#Potentially use Essie's finish categories and parse descriptions to get finish types
#Or more easily, for product_type, select each color and finish
#Use Selenium to automate these selections and parse website


# In[ ]:


url = "https://www.opi.com/collections/shop-products?color=Red&finish=Cr%C3%A8me&product-type=Nail%20Lacquer"


# In[ ]:


#https://www.opi.com/collections/shop-products
#https://www.opi.com/collections/nail-colors
#https://selenium-python.readthedocs.io/locating-elements.html
driver = webdriver.Chrome()
driver.get('https://www.opi.com/collections/shop-products')
time.sleep(10)

#XPATH: //*[@id="main"]/section[2]/div/div/div[1]/button 
next_btn = driver.find_element(By.XPATH, "//*[@id='button--:r0:--3']")
next_btn.click()


# In[ ]:


#attrs_by_prod = [prod.attrs for prod in polish_list]
#type(polish_list[0])
#polish_list[0].to_dict()
#attrs_by_prod
#data-color-system = Collection
#Add collection and product name to attrs_by_prod
#Gay movie analysis: How have top titles changed for Rotten Tomatoes over time? 
#https://www.rottentomatoes.com/browse/tv_series_browse/genres:lgbtq~sort:popular


# In[2]:


#Function to get attributes for each item in OPI website
import time

def get_each_by_opi_product_tag(driver):
    #driver.get(url_to_scrape)
    #time.sleep(10)
    html_doc = driver.page_source
    #print(html_doc)
    soup = BeautifulSoup(html_doc, 'html.parser')
    polish_list = soup.find_all("a", "productCard__titles")  #find_all also gets descendents
    return polish_list

def get_attrs_for_product(prod_dict):
    return dict((k, prod_dict[k]) for k in attrs_to_parse)

def get_product_type_and_name(prod_tag):
    #getting Product Type and Product names, using contents
    #https://stackoverflow.com/questions/25251841/bs4-getting-text-in-tag
    return {'product-type': prod_tag.contents[0].text, 
            'product-name': prod_tag.contents[1].text}

    


# In[3]:


#For all prods in polish_list, get below attrs and parse for Product Type/Product Name
attrs_to_parse = ['data-color-family-primary',
 #'data-color-family-secondary',
 'data-color-subgroup',
 'data-color-finish',
 #'data-color-depth',
 #'data-color-hex',
 'data-color-system',
'href' #will use hrefs to later parse descriptions for each product, opi.com/products/href[-1]
]

#polish_list[0].attrs


# In[4]:


import random
import time

def get_attrs_by_product(driver):
    product_tags = get_each_by_opi_product_tag(driver)
    attrs_by_prod = [get_attrs_for_product(prod.attrs) | get_product_type_and_name(prod) for prod in product_tags]
    return attrs_by_prod


# In[5]:


# driver = webdriver.Chrome()
# #url_to_scrape = 'https://www.opi.com/collections/shop-products?color=Red&finish=Cr%C3%A8me&product-type=Nail%20Lacquer'
# url_to_scrape = 'https://www.opi.com/collections/shop-products?product-type=Nail%20Lacquer--Infinite%20Shine'

# # try:
# #     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()
# #     time.sleep(random.random()*10)
# #     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[4]/section/div[2]/button'))).click()
# #     time.sleep(random.random()*10)
# # except:
# #     driver.quit()

# #time.sleep(random.random()*10)
# #print(get_attrs_by_product(driver, url_to_scrape))
# #driver.quit()


# In[13]:


#polish_list[0]['data-color-finish']
#Using Selenium to click "Show More" button
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import json
from random import randint


#Dismiss cookies window
#https://stackoverflow.com/questions/64032271/handling-accept-cookies-popup-with-selenium-in-python
#https://stackoverflow.com/questions/59130200/selenium-wait-until-element-is-present-visible-and-interactable

#Div id: onetrust-button-group
#button id: onetrust-reject-all-handler
#onetrust-accept-btn-handler

#//*[@id="main"]/div[4]/section/div[2]/button

def click_show_more_btn(driver, url_has_page_number=False):
    time.sleep(randint(15, 20))
    #if url_has_page_number, there will be two load buttons and the xpath is different
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
        #Dismiss cookies pop-up
        WebDriverWait(driver, randint(10, 15)).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()
    
        #if end_page is None, click thru until the last page
        if end_page is None:
            while True:
                try:
                    click_show_more_btn(driver, url_has_page_number)
                except TimeoutException:
                    break

        else:
            num_clicks = end_page-start_page
            #Click show-more button
            for i in range(num_clicks):
                click_show_more_btn(driver, url_has_page_number)
        
        #Get product results
        time.sleep(randint(30, 40))
        prods = get_attrs_by_product(driver)
        #Write results to json file
        end_page = 25
        output_file = f"opi_products_pages_{start_page}_thru_{end_page}.json"
        with open(output_file, 'w') as fp:
            json.dump(prods, fp)
        driver.close()
        
    except Exception as e:
        print(e)
        driver.quit()
    
#get_products_from_site(num_pages_to_parse=5)
#get_products_from_site(start_page=6, end_page=10)
#get_products_from_site(start_page=11, end_page=15)
#get_products_from_site(start_page=16, end_page=20)
get_products_from_site(start_page=1)

                                
# accept_cookies_btn = driver.find_element(By.ID, 'onetrust-reject-all-handler')
# accept_cookies_btn.click()


#show_more_button = driver.find_element(By.CLASS_NAME, 'Button_button__v0_QK')
#show_more_button.click()
#Cookies window appears to be in the way
#https://stackoverflow.com/questions/43868009/how-to-resolve-elementnotinteractableexception-element-is-not-visible-in-seleni


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




