# capstone project 
## basicc folder structure:
Zepto-Data-AI-Platform/
|__ data_pipeline/
    |__ __pycache__/
    |__ output_data/
        |__ raw_books_data.csv
        |__ clean_data.csv
    |__ database
        |__
    |__ data_pipeline_workflow.ipynb
    |__ data_scraper.py
    |__ database.py
    |__ database.sql
    |__ database_check_functions.py
|__ analytics/
|__ support_assistant
|__ .gitignore
|__ readme.md
|__ config.py

## module 1 - data pipeline:

### 1. description
1. The main ile working for this is data_pipelin_workflow.ipynb
2. Depending on the workflow of this, the module works. Various functions are called by importing modules and the workflow is executed.
3. The workflow is explained as-- 
    3.1. Scrape data using config details 
        files used: data_scraper.py
    3.2. clean this data and convert price from gbp to INR as per rate in config
        files used: data_cleaner.py
    3.3. create the tables by using database.py (which inturn calls database.sql)
        files used: database.py, database.sql
    3.4 Insert into data using pandas df
        files used: database.py
    3.5 Execute various queries to analyze the data and check if all conditions given by project are met.
        files used: queries_for_analysis.py


### 2. Detailed working of each file
step 1: data_scraper.py
    - 1. GET WEB PAGE
    - 2. GET ALL CATEGORIES
    - 3. GET BOOK COUNT FOR A CATEGORY
    - 4. FIND 3 CATEGORIES WITH >30 BOOKS
    - 5. SCRAPE BOOKS FROM ONE PAGE
    - 6. SCRAPE COMPLETE CATEGORY

    returns: df, selected_categories, df.shape

step 2: data_cleaner.py
    - 1. clean rating
    - 2. clean price column
    - 3. clean availability column
    - 4. convert price from GBP to INR

step 3: database.py
    - 1. create and connect to database named library_collection
    - 2. prepare 3 dataframes - books, availability and category
    - 3. creation of tables uses database.sql. After creating, insert into  DB

step 4: queries_for_analysis.py
    - 1. DECLARE ALL SQL QUERIES
    - 2. DEFINE HELPER FUNCTIONS
    - 3. MAIN CHECK FUNCTION
            This function is called by workflow file which inturn calls other functions and completes the analysis.

## module 2 - analytics:

### 1. description


### 2. Detailed working of each file


## module 3 - support assistant:

### 1. description


### 2. Detailed working of each file

## git ignore

## config file