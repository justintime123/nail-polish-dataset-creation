# Nail Polish Dataset Creation 💅

## Project Overview

**Goal:** Collect and standardize data on nail polish between different companies to be compared. <br>

**Research Question:** How do the distributions of colors and finishes differ between companies? 

## Data
### Acquisition
- I scraped data from the following companies using Python and Selenium.
  - [OPI](https://www.opi.com/)
  - [Morgan Taylor](https://gelish.com/)
### Legal Disclaimer on Webscraping
- This project is only to be used for personal / demonstrational purposes (not commercial).
- According to [_hiQ Labs, Inc v LinkedIn_](https://techcrunch.com/2022/04/18/web-scraping-legal-court/), scraping public data is legal. However, there are a few important conduct notes for webscraping:
  -  Respect the company's robots.txt file. This file set rules and limitations for web-scraping and crawling.
     - [Overview of robots.txt files](https://yoast.com/ultimate-guide-robots-txt/)
     - [How to read robots.txt files](https://www.zenrows.com/blog/robots-txt-web-scraping#most-common-robots-txt-rules) 
  -  Don't overload servers.
  -  Requests shouldn't harm the function/operation of the website.
 
### Transformation
:star: Wrote Regex to parse fields from alt-text of Morgan Taylor products. <br><br>
:star: Used K-means algorithm to determine dominant colors in product images. <br>
- This was used to standardize color families between different brands.
   
### Standardization
I formatted data into the following format:

| Column name | Description 
| ----------- | ----------- 
Brand | Nail polish brand (OPI or Morgan Taylor)
Product Name | Name of the polish 
Product Type | Nail Lacquer, Vegan
Color family | Primary/base color 
Primary finish | Creme, metallic, glitter, shimmer, pearl, etc. Covers any effects (like jelly).
Link | link to the product page

## Data Visualization via Dash App


https://github.com/user-attachments/assets/6b4d1845-a3ed-4de8-9f49-3a340a7f308e



## Technologies and Libraries
- Python:
  - Selenium
  - BeautifulSoup
  - Pandas
  - Dash 


## Code structure 
- webscrapers
  - get raw data from websites and dump into json files
- data transformation
  - transform data to conform to standardized df_format file
- data exploration
