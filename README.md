# Nail Polish Dataset Creation 💅

## Disclaimer: Only to be used for educational / demonstrational purposes

## Project Overview

**Goal:** Collect and standardize data on nail polish between different companies to be compared. <br>

**Research Question:** How do the distributions of colors and finishes differ between companies? 

## Data
### Acquisition
- I scraped data from the following companies using Python and Selenium.
  - [OPI](https://www.opi.com/)
  - [Morgan Taylor](https://gelish.com/)
- I followed each company's robots.txt file. These files set rules and limitations for web-scraping and crawling.
  - To see a robots.txt file for a given website, append '/robots.txt' to the website's root directory (e.g., https://www.opi.com/robots.txt)
  - For more info, see the below links
    - [Overview of robots.txt files](https://yoast.com/ultimate-guide-robots-txt/)
    - [How to read robots.txt files](https://www.zenrows.com/blog/robots-txt-web-scraping#most-common-robots-txt-rules) <br><br>
   
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



## Technologies and Libraries
- Python: Selenium, BeautifulSoup, Pandas 


## Code structure (TODO: add diagram to show flow)
- webscrapers
  - get raw data from websites and dump into json files
- data transformation
  - transform data to conform to standardized df_format file
- data standardization
  - In Progress
- Database storage (TBD)
  - Potentially use SQLLite
