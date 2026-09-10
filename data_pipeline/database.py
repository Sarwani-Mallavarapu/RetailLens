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
    dataframe.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )
    connection.commit()
    print(f"{len(dataframe)} records inserted into '{table_name}'.")


def execute_query(connection, query, parameters=None):
    """Executes a parameterized SQL query."""
    cursor = connection.cursor()
    if parameters is None:
        cursor.execute(query)
    else:
        cursor.execute(query, parameters)
    connection.commit()
    return cursor


def normalize_column(dataframe, column_name):
    """Creates a mapping between unique values and integer IDs."""
    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    unique_values = dataframe[column_name].dropna().unique()
    sorted_unique_values = sorted(unique_values)
    normalized_data = {
        value: index
        for index, value in enumerate(sorted_unique_values, start=1)
    }
    return normalized_data


def get_normalized_data_to_insert(dataframe, columns_to_normalize):
    """Normalizes specified columns in a DataFrame."""
    normalized_dataframe = dataframe.copy()
    normalization_mappings = {}

    for column in columns_to_normalize:
        if column not in normalized_dataframe.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        normalization_mapping = normalize_column(
            normalized_dataframe,
            column
        )
        normalized_dataframe[column] = (
            normalized_dataframe[column].map(normalization_mapping)
        )
        normalization_mappings[column] = normalization_mapping
    return normalized_dataframe, normalization_mappings


def prepare_master_dataframe(dataframe, source_column, database_column):
    """Creates a DataFrame containing unique values for a master table."""
    if source_column not in dataframe.columns:
        raise ValueError(f"Column '{source_column}' not found in DataFrame.")
    master_dataframe = (
        dataframe[[source_column]]
        .dropna()
        .drop_duplicates()
        .rename(columns={source_column: database_column})
        .reset_index(drop=True)
    )
    # print("\n\nprinting master df")
    # print(master_dataframe)
    return master_dataframe


def get_master_mapping(connection, table_name, id_column, value_column):
    """Retrieves the ID/value mapping from a master table."""
    query = f"""
        SELECT {id_column}, {value_column}
        FROM {table_name}
    """
    cursor = execute_query(connection, query)

    mapping_dict={
        value: record_id
        for record_id, value in cursor.fetchall()
    }
    # print("mapping_dict-->", mapping_dict)
    return mapping_dict


def insert_master_data(
    connection,
    dataframe,
    source_column,
    table_name,
    database_column
):
    """Inserts unique values into a master table and returns their IDs."""
    master_dataframe = prepare_master_dataframe(
        dataframe,
        source_column,
        database_column
    )

    if master_dataframe.empty:
        return {}, master_dataframe

    insert_data(
        connection,
        master_dataframe,
        table_name
    )

    id_column = "id"

    return get_master_mapping(
        connection,
        table_name,
        id_column,
        database_column
    ), master_dataframe

def prepare_books_dataframe(dataframe, category_mapping, availability_mapping):
    """Prepares the books DataFrame according to the books table schema."""

    books_dataframe = dataframe.copy()

    # Convert rating words to integer values
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

    # Map category names to category IDs
    books_dataframe["category_id"] = (
        books_dataframe["category"].map(category_mapping)
    )

    # Map availability text to availability IDs
    books_dataframe["availability_id"] = (
        books_dataframe["availability"].map(availability_mapping)
    )

    # Rename price column to match database schema
    books_dataframe.rename(
        columns={"price_GBP": "price_gbp"},
        inplace=True
    )

    # Select only columns required by books table
    books_dataframe = books_dataframe[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "category_id",
            "availability_id"
        ]
    ]

    return books_dataframe


def insert_data_into_all_tables(dataframe):
    """Inserts scraped data into all normalized tables."""
    connection = create_and_connect_to_database()

    try:
        category_mapping, category_dataframe = insert_master_data(
            connection,
            dataframe,
            "category",
            "category_master",
            "category"
        )

        availability_mapping, availability_dataframe = insert_master_data(
            connection,
            dataframe,
            "availability",
            "availability_master",
            "availability"
        )

        books_dataframe = prepare_books_dataframe(
            dataframe,
            category_mapping,
            availability_mapping
        )

        insert_data(
            connection,
            books_dataframe,
            "books"
        )

        print("All data inserted successfully!")

    finally:
        close_database_connection(connection)
        return category_dataframe, availability_dataframe, books_dataframe


def normalise_and_insert_data(
    dataframe,
    columns_to_normalize=None,
    table_name=None
):
    """Runs the complete database creation and data-loading workflow."""
    create_required_tables()
    category_dataframe, availability_dataframe, books_dataframe=insert_data_into_all_tables(dataframe)
    print("Database loading completed successfully!")
    return category_dataframe, availability_dataframe, books_dataframe

# df=pd.read_csv("D:\\Masai\\CapstoneProject\\Zepto-Data-AI-Platform\\data_pipeline\\output_data\\cleaned_data.csv")
# normalise_and_insert_data(dataframe=df)