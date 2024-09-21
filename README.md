# The Nail Polish Db 💅

## Project Overview

**Goal:** Collect and standardize data on nail polish between different companies to be compared. <br>

**Research Question:** How do the distributions of colors and finishes differ between companies? 

## Data
### Acquisition
- I scraped data from the following companies using Python and Selenium.
  - [Sally Hansen](https://www.sallyhansen.com/en-us) 
  - [OPI](https://www.opi.com/)
  - [Morgan Taylor](https://gelish.com/)
- I followed each company's robots.txt file. These files set rules and limitations for web-scraping and crawling.
  - To see a robots.txt file for a given website, append '/robots.txt' to the website's root directory (e.g., https://www.opi.com/robots.txt)
  - For more info, see the below links
    - [Overview of robots.txt files](https://yoast.com/ultimate-guide-robots-txt/)
    - [How to read robots.txt files](https://www.zenrows.com/blog/robots-txt-web-scraping#most-common-robots-txt-rules) <br><br>
   
### Standardization
I formatted data into the following format:

| Column name | Description | Sample values
| ----------- | ----------- | -------------



## Technologies and Libraries
- Python: Selenium, BeautifulSoup, Pandas 


## Code structure (TODO: add diagram to show flow)
- webscrapers
  - get raw data from websites and dump into json files
- data transformation
  - transform data to conform to standardized df_format file
- data standardization
  - step 1: Data exploration (exploring data for each company and potentially standardizing)
  - step 2: standardizing data
- Database storage (TBD)
  - Potentially use SQLLite
