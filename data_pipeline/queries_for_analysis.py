import database as db
import config as cfg
import pandas as pd


sql_file_path = cfg.FUNCTIONS_CHECK_SQL_FILE_PATH


# SQL QUERIES
# --------------------------------------------------

count_of_books_query = "SELECT COUNT(*) AS total_books " \
                       "FROM books"


count_of_available_books_query = "SELECT COUNT(*) AS available_books " \
                                 "FROM books b "\
                                 "WHERE availability = True"


count_of_5_rated_books_query = "SELECT COUNT(*) AS five_star_books " \
                               "FROM books b " \
                               "WHERE b.rating = 5"


top_5_expensive_books_query = "SELECT title, price_gbp, price_inr " \
                              "FROM books " \
                              "ORDER BY price_gbp DESC " \
                              "LIMIT 5"


average_rating_by_category_query = "SELECT c.category, " \
                                   "AVG(b.rating) AS average_rating " \
                                   "FROM books b " \
                                   "JOIN category_master c " \
                                   "ON b.category_id = c.id " \
                                   "GROUP BY c.category " \
                                   "ORDER BY average_rating DESC"


top_3_books_per_category_query = "SELECT c.category, b.title, b.rating " \
                                 "FROM books b " \
                                 "JOIN category_master c " \
                                 "ON b.category_id = c.id " \
                                 "WHERE b.id IN ( " \
                                 "    SELECT id " \
                                 "    FROM ( " \
                                 "        SELECT id, " \
                                 "               ROW_NUMBER() OVER ( " \
                                 "                   PARTITION BY category_id " \
                                 "                   ORDER BY rating DESC, title ASC " \
                                 "               ) AS rn " \
                                 "        FROM books " \
                                 "    ) ranked_books " \
                                 "    WHERE rn <= 3 " \
                                 ") " \
                                 "ORDER BY c.category, b.rating DESC, b.title ASC"


# JOIN query used for comparison with pandas.merge()
all_joined_data_query = (
    "SELECT "
    "b.title, "
    "b.price_gbp, "
    "b.price_inr, "
    "b.rating, "
    "c.category, "
    "b.availability "
    "FROM books b "
    "JOIN category_master c "
    "ON b.category_id = c.id "
    "ORDER BY c.category, b.rating DESC, b.title ASC"
)


# DISTINCT requirement
distinct_categories_query = "SELECT DISTINCT category " \
                            "FROM category_master " \
                            "ORDER BY category"


# Additional IN requirement
books_with_selected_ratings_query = "SELECT title, rating " \
                                    "FROM books " \
                                    "WHERE rating IN (4, 5) " \
                                    "ORDER BY rating DESC, title ASC"


# Queries used to validate individual tables
select_all_books_query = "SELECT * FROM books"

select_all_categories_query = "SELECT * FROM category_master"




# HELPER FUNCTIONS
# --------------------------------------------------

def add_id_to_dataframes(df):
    """Adds sequential IDs to a DataFrame for comparison with database tables."""
    df = df.copy()
    df["id"] = df.index + 1
    return df


def prepare_pandas_join_result(
    books_dataframe,
    category_dataframe
):
    """Reproduces the SQL JOIN using pandas.merge()."""

    merged_dataframe = pd.merge(
        books_dataframe,
        category_dataframe,
        left_on="category_id",
        right_on="id",
        how="left"
    )

    merged_dataframe = merged_dataframe[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "category",
            "availability"
        ]
    ]

    return merged_dataframe

def standardize_join_result(df):
    """Standardizes JOIN results before comparing DataFrames."""

    df = df.copy()

    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "category",
            "availability"
        ]
    ]

    df = df.sort_values(
        by=["category", "rating", "title"]
    ).reset_index(drop=True)

    return df


# MAIN CHECK FUNCTION
# --------------------------------------------------

def execute_checks_and_queries(
    category_dataframe,
    books_dataframe,
    cleaned_data
):
    """Executes database checks, SQL queries and pandas merge validation."""

    # Add IDs for comparison with database-generated IDs
    category_dataframe = add_id_to_dataframes(category_dataframe)
    books_dataframe = add_id_to_dataframes(books_dataframe)

    connection = db.create_and_connect_to_database()

    try:

        
        # 01 - COUNT OF BOOKS
        # --------------------------------------------------

        print("\n\n")
        print("01 --------------------------------------------------")

        df = pd.read_sql_query(
            count_of_books_query,
            connection)
        print(f"Number of records in 'books' table: "   f"{df.iloc[0, 0]}")

        
        # 02 - COUNT OF AVAILABLE BOOKS
        # --------------------------------------------------

        print("\n02 --------------------------------------------------")

        df = pd.read_sql_query(
            count_of_available_books_query,
            connection)
        print(f"Number of available books: "   f"{df.iloc[0, 0]}")

        
        # 03 - COUNT OF 5-RATED BOOKS
        # --------------------------------------------------

        print("\n03 --------------------------------------------------")

        df = pd.read_sql_query(
            count_of_5_rated_books_query,
            connection)
        print(f"Number of 5-rated books: "   f"{df.iloc[0, 0]}")

        
        # 04 - TOP 5 EXPENSIVE BOOKS
        # --------------------------------------------------

        print("\n04 --------------------------------------------------")

        df = pd.read_sql_query(
            top_5_expensive_books_query,
            connection)
        print("Top 5 most expensive books:")
        print(df)


        
        # 05 - AVERAGE RATING BY CATEGORY
        # --------------------------------------------------

        print("\n05 --------------------------------------------------")

        df = pd.read_sql_query(
            average_rating_by_category_query,
            connection)
        print("Average rating by category:")
        print(df)


        
        # 06 - TOP 3 BOOKS PER CATEGORY
        # --------------------------------------------------

        print("\n06 --------------------------------------------------")

        df = pd.read_sql_query(
            top_3_books_per_category_query,
            connection)
        print("Top 3 rated books per category:")
        print(df)


        
        # 07 - DISTINCT CATEGORIES
        # --------------------------------------------------

        print("\n07 --------------------------------------------------")

        df = pd.read_sql_query(
            distinct_categories_query,
            connection)
        print("Distinct categories:")
        print(df)


        
        # 08 - BOOKS WITH RATINGS 4 OR 5
        # --------------------------------------------------

        print("\n08 --------------------------------------------------")

        df = pd.read_sql_query(
            books_with_selected_ratings_query,
            connection)
        print("Books with ratings 4 or 5:")
        print(df)


        
        # 09 - INDIVIDUAL TABLE VALIDATION
        # --------------------------------------------------

        print("\n09 --------------------------------------------------")

        query_op_books = pd.read_sql_query(
            select_all_books_query,
            connection)
        query_op_categories = pd.read_sql_query(
            select_all_categories_query,
            connection)

        print("Checking if individual database tables "   "and DataFrames are equal...")
        print("Are the two books DataFrames equal? ",   query_op_books.equals(books_dataframe))
        print("Is length of books table and books DataFrame equal? ",   len(query_op_books) == len(books_dataframe))
        print("Are the two category DataFrames equal? ",   query_op_categories.equals(category_dataframe))
        print("Is length of category table and category DataFrame equal? ",   len(query_op_categories) == len(category_dataframe))
        
        
        # 10 - SQL JOIN VS PANDAS MERGE
        # --------------------------------------------------

        print("\n10 --------------------------------------------------")

        print("Checking SQL JOIN result against pandas.merge() result...")

        # SQL JOIN result
        query_op_all_join = pd.read_sql_query(
            all_joined_data_query,
            connection)
        # pandas.merge() result
        pandas_merge_result = prepare_pandas_join_result(
            books_dataframe,
            category_dataframe
            )
        # Standardize both DataFrames
        sql_join_result = standardize_join_result(
            query_op_all_join)
        pandas_merge_result = standardize_join_result(
            pandas_merge_result)
        print("\nSQL JOIN result:")
        print(sql_join_result)

        print("\nPandas merge() result:")
        print(pandas_merge_result)

        print("\nAre SQL JOIN and pandas.merge() results equal? ",   sql_join_result.equals(pandas_merge_result))
        print("Is length of SQL JOIN result and pandas.merge() result equal? ",   len(sql_join_result) == len(pandas_merge_result))

        
        # 11 - CLEANED DATA VS DATABASE
        # --------------------------------------------------

        print("\n11 --------------------------------------------------")

        print("Are all books in cleaned_data present in the database?",   len(cleaned_data) == len(query_op_books))
        print("Are all cleaned books present in pandas.merge() result?",   len(cleaned_data) == len(pandas_merge_result))
        print("Number of cleaned books: ",   len(cleaned_data))
        print("Number of books in database: ",   len(query_op_books))
        print("Number of categories: ",   len(category_dataframe))
        print("Database checks and query execution completed successfully.")

    finally:
        db.close_database_connection(connection)