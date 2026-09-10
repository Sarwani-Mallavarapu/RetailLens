# Zepto-Data-AI-Platform

## Module 1: Data Pipeline

This module builds a complete book data pipeline from a public e-commerce website, stores the raw data, cleans it, and loads it into a SQLite database for downstream analytics.

### Purpose

The pipeline is designed to:
- scrape book listings from the Books to Scrape website,
- select qualifying categories with a minimum number of books,
- save raw scraped data as CSV,
- clean and transform the dataset,
- convert GBP prices into INR,
- store the standardized dataset in SQLite tables.

---

### Folder Structure

```text
data_pipeline/
├── data_scraper.py          # Scrapes books and saves raw data
├── data_cleaner.py          # Cleans ratings, prices, availability, and INR conversion
├── database.py              # SQLite connection, schema execution, and inserts
├── database.sql             # Database schema for category and books tables
├── database/
│   └── library_collection.db  # SQLite database output
├── output_data/
│   ├── raw_books_data.csv
│   ├── books_by_category_raw_data.csv
│   └── cleaned_data.csv
├── data_pipeline_workflow.ipynb
├── query_tester.ipynb
├── x_data_scraper.py
└── __pycache__/
```

---

### Workflow

1. Scrape categories from the Books to Scrape homepage.
2. Filter categories that have more than 30 books.
3. Collect the first 3 qualifying categories.
4. Download all pages in each selected category.
5. Extract fields such as:
   - category
   - title
   - price
   - rating
   - availability
6. Save raw data to a CSV file.
7. Clean the dataset by:
   - converting rating words to numeric values,
   - removing currency symbols,
   - converting price to GBP float, 
   - converting availability to boolean values,
   - calculating INR price using the configured conversion rate.
8. Create the SQLite database and schema.
9. Insert normalized master data and book records into the database tables.

---

### Key Components

#### 1. `data_scraper.py`
This file handles the website scraping logic.

Main functions:
- `get_page(url)`
- `get_categories()`
- `get_category_book_count(category_url)`
- `find_qualifying_categories()`
- `scrape_books_from_page(soup, category)`
- `scrape_category(category, category_url)`
- `scrape_books()`

It uses the configured website URL and category thresholds from `config.py`.

#### 2. `data_cleaner.py`
This file cleans the scraped data.

Main functions:
- `convert_words_to_numbers(text)`
- `clean_ratings_data(dirty_data)`
- `clean_price_data(dirty_data)`
- `clean_availability_data(dirty_data)`
- `convert_gbp_to_inr(dirty_data)`
- `clean_books_data(raw_data)`

The cleaner ensures the dataset is ready for analytics and database insertion.

#### 3. `database.py`
This file manages the SQLite database workflow.

Main functions:
- `create_and_connect_to_database()`
- `close_database_connection(connection)`
- `execute_sql_file(connection, sql_file_path)`
- `create_required_tables()`
- `insert_data(connection, dataframe, table_name)`
- `prepare_master_dataframe(...)`
- `insert_master_data(...)`
- `prepare_books_dataframe(...)`
- `insert_data_into_all_tables(dataframe)`
- `normalise_and_insert_data(...)`

This is responsible for creating the schema, loading master tables, and storing the books dataset.

#### 4. `database.sql`
Defines the schema for:
- `category_master`
- `availability_master`
- `books`

The database keeps normalized dimension tables and a fact-style books table with foreign keys.

---

### Configuration

The pipeline settings are defined in `config.py`:

- `BASE_URL` = Books to Scrape website
- `NO_OF_CATEGORIES_TO_SCRAPE` = 3
- `MIN_BOOKS_PER_CATEGORY` = 30
- `GBP_TO_INR_CONVERSION_RATE` = 105.50
- `PIPELINES_OUTPUT_FOLDER`
- `PIPELINES_DATABASE_FOLDER`
- `DB_NAME` = `library_collection.db`

---

### Outputs

#### Raw Data
Stored in:
- `data_pipeline/output_data/books_by_category_raw_data.csv`

#### Cleaned Data
The cleaner produces a cleaned dataset with:
- numeric ratings,
- float GBP price,
- boolean availability,
- INR conversion column,
- ready-to-load table values.

#### Database
The SQLite database is created in:
- `data_pipeline/database/library_collection.db`

---

### Typical Usage

Run the scraper and pipeline in Python from the project root:

```python
import pandas as pd
import data_pipeline.data_scraper as scraper
import data_pipeline.data_cleaner as cleaner
import data_pipeline.database as db

raw_df = scraper.scrape_books()
clean_df = cleaner.clean_books_data(raw_df)
db.normalise_and_insert_data(clean_df)
```

If the module is imported as a package, adjust the import paths according to your project structure.

---

### Notes

- The scraper uses the Books to Scrape website and depends on the structure of that page.
- The pipeline is currently configured to collect exactly three categories that exceed the minimum threshold.
- The data pipeline is the foundation for analytics and downstream AI-driven insights in this project.

---

## Summary

The Data Pipeline module transforms raw scraped website data into a cleaned, structured, and database-ready dataset. It is the first core stage of the Zepto-Data-AI-Platform and supports analytics, reporting, and future AI integration.