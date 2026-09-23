# RetailLens

### Retail Analytics & AI Platform

RetailLens is an end-to-end retail data and AI platform for
data engineering, analytics, and AI-powered support.

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

## Module 2: Analytics

This module uses the Titanic dataset to demonstrate an end-to-end analytics workflow: exploratory analysis, data preparation, classification, regression, model comparison, and model persistence.

### Contents

```text
analytics/
├── data_profiler.ipynb                    # EDA, missing-data treatment, plots, and data story
├── analysis.ipynb                         # Modeling, evaluation, tuning, and artifact export
├── input_data/titanic.csv                 # Local fallback copy of the dataset
└── titanic_random_forest_pipeline.joblib  # Saved fitted preprocessing + Random Forest pipeline
```

### Workflow

1. `data_profiler.ipynb` loads Seaborn's Titanic dataset, with `input_data/titanic.csv` as an offline fallback.
2. It profiles shape, types, descriptive statistics, and missing-value rates. The workflow drops `deck` because of its high missing rate, drops the small number of rows missing embarkation values, and imputes `age` using the median age for each passenger class.
3. It explores age and fare distributions, IQR-based outliers, fare skewness, survival rates by sex and class, and a correlation heatmap for the six core numeric columns.
4. It adds a four-chart data story covering survival by sex, passenger class, their combination, and age; it also standardizes `age` and `fare` with `StandardScaler` for an exploratory check.
5. `analysis.ipynb` creates a stratified train/test split using `survived` as the target. Numeric features are median-imputed and scaled; categorical features are most-frequent-imputed and one-hot encoded inside a `ColumnTransformer`.
6. Logistic Regression, Decision Tree, and Random Forest classifiers are trained through complete scikit-learn pipelines and evaluated with confusion matrices, accuracy, precision, recall, F1, ROC curves, and AUC.
7. The Random Forest workflow compares baseline, `class_weight="balanced"`, and training-fold-only SMOTE strategies; performs `GridSearchCV` over Random Forest hyperparameters; and reports the out-of-bag score for the best estimator.
8. A separate linear-regression task predicts `fare`, reports MAE, RMSE, R², and adjusted R², and visualizes residuals. The final comparison keeps classification and regression metrics in separate metric groups.
9. The best fitted Random Forest pipeline is saved with Joblib and reloaded to verify that it can predict on raw feature input.

### Running the notebooks

Open and run the notebooks from the `analytics/` directory in this order:

1. `data_profiler.ipynb`
2. `analysis.ipynb`

The notebooks require common data-science packages including `pandas`, `numpy`, `seaborn`, `matplotlib`, `scikit-learn`, `imbalanced-learn`, and `joblib`.

---

## Module 3: Support Assistant

This module provides a policy-focused Zepto support assistant. It retrieves relevant policy documents from a persistent ChromaDB collection, uses a LangGraph workflow to route questions, and exposes a validated FastAPI endpoint.

### Contents

```text
support_assistant/
├── api.py                         # FastAPI application and POST /ask endpoint
├── graph.py                       # LangGraph state, routing, retrieval, and response schema
├── ingest.py                      # Embeds and stores the policy documents in ChromaDB
├── prompt_template.py             # Prompt for an optional future LLM implementation
├── docs/                          # Eight Zepto policy documents
├── chroma_db/                     # Persistent ChromaDB vector store
```

### How it works

1. Run `ingest.py` to load the eight text files in `docs/`, embed each document with `all-MiniLM-L6-v2`, and upsert them into the `zepto_support_docs` ChromaDB collection.
2. A request to `POST /ask` is passed to the compiled LangGraph workflow.
3. The graph classifies the query as a policy or general question. Policy-related queries are retrieved against the vector store (top three chunks); general queries receive a scope-limited response.
4. Responses conform to the `FinalAnswer` schema:

```json
{
  "answer": "...",
  "sources": ["doc_04"],
  "confidence": 1.0
}
```

The default `MOCK_LLM=1` mode uses deterministic keyword routing and returns a snippet from the best retrieved policy document. Setting `MOCK_LLM=0` preserves the same fallback behavior while leaving a clear extension point for a real LLM. `prompt_template.py` defines the grounded-answer prompt intended for that extension.

### Run the assistant

Install dependencies such as `fastapi`, `uvicorn`, `langgraph`, `chromadb`, `sentence-transformers`, and `pydantic`, then run these commands from the project root:

```powershell
python support_assistant/ingest.py
uvicorn support_assistant.api:app --reload
```

Example request:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ask `
  -ContentType 'application/json' `
  -Body '{"query":"How can I track my delivery?"}'
```

### Tested Answeres:
------------------------
PS CapstoneProject\Zepto-Data-AI-Platform> $response = Invoke-RestMethod `
>>     -Uri "http://127.0.0.1:8000/ask" `
>>     -Method POST `
>>     -ContentType "application/json" `
>>     -Body (@{ query = "How can I track my delivery?" } | ConvertTo-Json)
>> 
>> $response | Format-List *


answer     : Based on the retrieved context: Every Zepto 
             order shows a live rider-tracking map from 
             the moment it is packed until delivery, 
             accessible from the 'Track Order' screen. 
             Estimated delivery time updates 
             automatically as the rider move
sources    : {doc_04, doc_01, doc_02}
confidence : 1.0



PS CapstoneProject\Zepto-Data-AI-Platform>  $response = Invoke-RestMethod `
>>     -Uri "http://127.0.0.1:8000/ask" `
>>     -Method POST `
>>     -ContentType "application/json" `
>>     -Body (@{ query = "What is the weather today?" } | ConvertTo-Json)
>> 
>> $response | ConvertTo-Json -Depth 5
{
    "answer":  "I can only answer questions about Zepto policies right now.",
    "sources":  [

                ],
    "confidence":  1.0
}

The available policy topics cover delivery, returns and refunds, membership, order tracking, cancellation, damaged or missing items, gift cards, and customer-support hours. The API documentation is available at `http://127.0.0.1:8000/docs` while the server is running.

---

## Summary

The platform is organized into three modules: a book-data pipeline that produces structured SQLite data, a Titanic analytics workflow that demonstrates EDA and predictive modeling, and a policy-based Zepto support assistant that offers retrieval-backed API responses.
