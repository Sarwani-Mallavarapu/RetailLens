import sqlite3
import pandas as pd
import config as cfg


db_folder_path = cfg.PIPELINES_DATABASE_FOLDER
db_name = cfg.DB_NAME
sql_file_path = cfg.SQL_FILE_PATH

print(f"Database folder path: {db_folder_path}")


def create_and_connect_to_database():
    """
    Creates the SQLite database file if it does not exist
    and connects to it.
    """
    db_path = db_folder_path / db_name

    connection = sqlite3.connect(db_path)

    # Enable foreign key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    print("Database connected!")

    return connection


def close_database_connection(connection):
    """Closes the SQLite database connection."""
    connection.close()
    print("Database connection closed!")


def execute_sql_file(connection, sql_file_path):
    """Reads and executes all SQL statements from a SQL file."""

    with open(sql_file_path, "r", encoding="utf-8") as file:
        sql_script = file.read()

    connection.executescript(sql_script)
    connection.commit()


def create_required_tables():
    """Creates all required tables using the SQL schema file."""

    connection = create_and_connect_to_database()

    try:
        execute_sql_file(connection, sql_file_path)
        print("Required tables created successfully!")

    finally:
        close_database_connection(connection)


def insert_data(connection, dataframe, table_name):
    """Inserts a DataFrame into a SQLite table."""

    if dataframe.empty:
        print(f"No records to insert into '{table_name}'.")
        return

    dataframe.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )

    connection.commit()

    print(
        f"{len(dataframe)} records inserted into '{table_name}'."
    )


def execute_query(connection, query, parameters=None):
    """Executes a SQL query."""

    cursor = connection.cursor()

    if parameters is None:
        cursor.execute(query)
    else:
        cursor.execute(query, parameters)

    return cursor


def prepare_master_dataframe(
    dataframe,
    source_column,
    database_column
):
    """
    Creates a DataFrame containing unique values
    for a master table.
    """

    if source_column not in dataframe.columns:
        raise ValueError(
            f"Column '{source_column}' not found in DataFrame."
        )

    master_dataframe = (
        dataframe[[source_column]]
        .dropna()
        .drop_duplicates()
        .rename(
            columns={
                source_column: database_column
            }
        )
        .reset_index(drop=True)
    )

    return master_dataframe


def get_master_mapping(
    connection,
    table_name,
    id_column,
    value_column
):
    """Retrieves ID/value mappings from a master table."""

    query = f"""
        SELECT {id_column}, {value_column}
        FROM {table_name}
    """

    cursor = execute_query(connection, query)

    return {
        value: record_id
        for record_id, value in cursor.fetchall()
    }


def insert_master_data(
    connection,
    dataframe,
    source_column,
    table_name,
    database_column
):
    """
    Inserts unique values into a master table
    and returns the ID mapping.
    """

    master_dataframe = prepare_master_dataframe(
        dataframe,
        source_column,
        database_column
    )

    if master_dataframe.empty:
        return {}, master_dataframe

    # Check existing master values
    existing_mapping = get_master_mapping(
        connection,
        table_name,
        "id",
        database_column
    )

    # Insert only values that do not already exist
    new_values = master_dataframe[
        ~master_dataframe[database_column].isin(
            existing_mapping.keys()
        )
    ]

    if not new_values.empty:
        insert_data(
            connection,
            new_values,
            table_name
        )

    # Get complete mapping after insertion
    complete_mapping = get_master_mapping(
        connection,
        table_name,
        "id",
        database_column
    )

    return complete_mapping, master_dataframe


def prepare_books_dataframe(
    dataframe,
    category_mapping
):
    """
    Prepares the books DataFrame according to the
    books table schema.

    Availability is stored directly as a boolean column.
    No availability master table is used.
    """

    books_dataframe = dataframe.copy()

    # -------------------------------------------------
    # Convert rating words to integer values
    # -------------------------------------------------

    if "rating" in books_dataframe.columns:

        if books_dataframe["rating"].dtype == "object":

            books_dataframe["rating"] = (
                books_dataframe["rating"]
                .map({
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5
                })
            )

    elif "star_rating" in books_dataframe.columns:

        books_dataframe.rename(
            columns={
                "star_rating": "rating"
            },
            inplace=True
        )

        if books_dataframe["rating"].dtype == "object":

            books_dataframe["rating"] = (
                books_dataframe["rating"]
                .map({
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5
                })
            )

    else:
        raise ValueError(
            "Expected either 'rating' or 'star_rating' column."
        )

    # -------------------------------------------------
    # Map category name to category ID
    # -------------------------------------------------

    books_dataframe["category_id"] = (
        books_dataframe["category"].map(category_mapping)
    )

    if books_dataframe["category_id"].isna().any():
        raise ValueError(
            "Some categories could not be mapped to category IDs."
        )

    # -------------------------------------------------
    # Convert availability to boolean
    # -------------------------------------------------

    if "availability" not in books_dataframe.columns:
        raise ValueError(
            "Column 'availability' not found in DataFrame."
        )

    books_dataframe["availability"] = (
        books_dataframe["availability"]
        .astype(bool)
    )

    # -------------------------------------------------
    # Rename price column
    # -------------------------------------------------

    if "price_GBP" in books_dataframe.columns:

        books_dataframe.rename(
            columns={
                "price_GBP": "price_gbp"
            },
            inplace=True
        )

    # -------------------------------------------------
    # Select final books table columns
    # -------------------------------------------------

    books_dataframe = books_dataframe[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "availability",
            "category_id"
        ]
    ]

    return books_dataframe


def insert_data_into_all_tables(dataframe):
    """
    Inserts scraped data into all normalized tables.

    Availability is stored directly in the books table.
    """

    connection = create_and_connect_to_database()

    category_dataframe = pd.DataFrame()
    books_dataframe = pd.DataFrame()

    try:

        # -------------------------------------------------
        # Category master
        # -------------------------------------------------

        category_mapping, category_dataframe = (
            insert_master_data(
                connection,
                dataframe,
                "category",
                "category_master",
                "category"
            )
        )

        # -------------------------------------------------
        # Books
        # -------------------------------------------------

        books_dataframe = prepare_books_dataframe(
            dataframe,
            category_mapping
        )

        insert_data(
            connection,
            books_dataframe,
            "books"
        )

        print("All data inserted successfully!")

        return category_dataframe, books_dataframe

    finally:
        close_database_connection(connection)


def normalise_and_insert_data(
    dataframe,
    columns_to_normalize=None,
    table_name=None
):
    """
    Runs the complete database creation
    and data-loading workflow.
    """

    create_required_tables()

    category_dataframe, books_dataframe = (insert_data_into_all_tables(dataframe))
    print("Database loading completed successfully!")
    return category_dataframe, books_dataframe