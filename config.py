from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_PIPELINE_ROOT = PROJECT_ROOT / "data_pipeline"

PIPELINES_OUTPUT_FOLDER = DATA_PIPELINE_ROOT / "output_data"

BASE_URL = "https://books.toscrape.com/"

NO_OF_PAGES = 8

NO_OF_CATEGORIES_TO_SCRAPE = 3

MIN_BOOKS_PER_CATEGORY = 30

GBP_TO_INR_CONVERSION_RATE = 105.50

PIPELINES_DATABASE_FOLDER = DATA_PIPELINE_ROOT / "database"

DB_NAME = "library_collection.db"

SQL_FILE_PATH = DATA_PIPELINE_ROOT / "database.sql"

FUNCTIONS_CHECK_SQL_FILE_PATH = DATA_PIPELINE_ROOT / "database_check_functions.sql"