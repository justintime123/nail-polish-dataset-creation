Nail polish passion project 

Goal: Collect and standardize data on nail polish between different companies to be compared. 
Research question: How do the distributions of colors and finishes differ between companies? 

Data Acquisition: I web-scraped data from several company sites using Python and Selenium.
Notes on robots.txt files / webscraping:
-I followed the robots.txt file for each company (Sally Hansen, OPI and Morgan Taylor)

Technologies:
-Python

Useful libraries:
-Selenium

Code structure (TODO: add diagram to show flow)
-webscrapers
..get raw data from websites and dump into json files
-data transformation
..transform data to conform to standardized df_format file
-data standardization
..step 1: Data exploration (exploring data for each company and potentially standardizing)
..step 2: standardizing data
-Database storage (TBD)
..Potentially use SQLLite
