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
   
### Standardization
I formatted data into the following format:

| Column name | Description 
| ----------- | ----------- 
Brand | Nail polish brand (OPI or Morgan Taylor)
Product Name | Name of the polish 
Product Type | Nail Lacquer, Vegan
Color family | Primary/base color 
Color shade | More detailed description of color (e.g., light blue) (optional)
Primary finish | Creme, metallic, glitter, shimmer, pearl, etc. Covers any effects (like jelly).
Secondary finish | Extra finish, if there's another on top
Original description | Optional field (if applicable) to show where color_shade, primary_finish, and secondary_finish were derived from
Link | link to the product page

## Data Exploration via Dash App


## Technologies and Libraries
- Python:
  - Selenium
  - BeautifulSoup
  - Pandas
  - Dash 


## Code structure (TODO: add diagram to show flow)
- webscrapers
  - get raw data from websites and dump into json files
- data transformation
  - transform data to conform to standardized df_format file
- data standardization
  - In Progress
- Database storage (TBD)
  - Potentially use SQLLite
