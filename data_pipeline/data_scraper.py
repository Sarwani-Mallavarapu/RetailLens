import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import config as cfg


# ---------------------------------------------------------
# 1. GET WEB PAGE
# ---------------------------------------------------------

def get_page(url):
    """
    Send HTTP request and return BeautifulSoup object.
    """

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


# ---------------------------------------------------------
# 2. GET ALL CATEGORIES
# ---------------------------------------------------------

def get_categories():
    """
    Scrape all available book categories from the website.
    """

    soup = get_page(cfg.BASE_URL)
    categories = {}
    category_links = soup.select("div.side_categories ul li ul li a")

    for link in category_links:
        category_name = link.get_text(strip=True)
        category_url = urljoin(cfg.BASE_URL,link["href"])
        categories[category_name] = category_url
    return categories


# ---------------------------------------------------------
# 3. GET BOOK COUNT FOR A CATEGORY
# ---------------------------------------------------------

def get_category_book_count(category_url):
    """
    Determine the number of books available
    in a category.
    """

    soup = get_page(category_url)
    result_count = soup.select_one( "form.form-horizontal strong")

    if result_count:
        return int(result_count.get_text(strip=True))
    return 0


# ---------------------------------------------------------
# 4. FIND 3 CATEGORIES WITH >30 BOOKS
# ---------------------------------------------------------

def find_qualifying_categories():
    """
    Dynamically find three categories
    containing more than 30 books.
    """

    categories = get_categories()
    qualifying_categories = {}
    #print("\nChecking categories...\n")
    for category_name, category_url in categories.items():
        try:
            book_count = get_category_book_count(category_url)
            #print(f"{category_name}: ", f"{book_count} books")
            if book_count > cfg.MIN_BOOKS_PER_CATEGORY:
                qualifying_categories[category_name] = {"url": category_url,"book_count": book_count}
            # Stop after finding 3
            # qualifying categories
            if len(qualifying_categories) == cfg.NO_OF_CATEGORIES_TO_SCRAPE:
                break
        except requests.RequestException as error:
            print(f"Failed to check ",f"{category_name}: {error}")
    return qualifying_categories


# ---------------------------------------------------------
# 5. SCRAPE BOOKS FROM ONE PAGE
# ---------------------------------------------------------

def scrape_books_from_page(soup, category):
    """
    Extract all books from the current page.
    """
    books = []
    products = soup.select( "article.product_pod"  )
    for product in products:
        # TITLE
        title_element = product.select_one("h3 a")
        title = title_element.get("title", "")
        # PRICE
        price_element = product.select_one("p.price_color")
        price = ""
        if price_element:
            price = price_element.get_text(strip=True)
        # RATING
        rating_element = product.select_one( "p.star-rating")
        rating = ""
        if rating_element:
            rating_classes = rating_element.get("class", [] )
            if len(rating_classes) > 1:
                rating = rating_classes[-1]
        # AVAILABILITY
        availability_element = product.select_one( "p.instock.availability")
        availability = ""
        if availability_element:
            availability = availability_element.get_text( strip=True)

        # STORE BOOK

        books.append({"category": category,"title": title,"rating": rating,"price": price,"availability": availability })

    return books


# ---------------------------------------------------------
# 6. SCRAPE COMPLETE CATEGORY
# ---------------------------------------------------------

def scrape_category(category,category_url):
    """
    Scrape every page of a category.
    """

    all_books = []
    current_url = category_url
    page_number = 1
    while current_url:
        #print( f"    Scraping ", f"{category} - ", f"Page {page_number}")
        try:
            soup = get_page(current_url )

        except requests.RequestException as error:
            #print( f"    Failed to scrape " ,f"{current_url}: {error}")
            break

        # ---------------------------------
        # Extract books from current page
        # ---------------------------------
        books = scrape_books_from_page( soup,  category)
        all_books.extend(books)

        # ---------------------------------
        # Find NEXT page
        # ---------------------------------
        next_button = soup.select_one("li.next a")
        if next_button:
            next_url = next_button.get(   "href")
            current_url = urljoin( current_url, next_url)
            page_number += 1
        else:current_url = None
    return all_books


# ---------------------------------------------------------
# 7. MAIN PIPELINE
# ---------------------------------------------------------

def scrape_books():

    # ---------------------------------
    # Find qualifying categories
    # ---------------------------------

    selected_categories = (find_qualifying_categories())

    # ---------------------------------
    # Safety check
    # ---------------------------------

    if len(selected_categories) < cfg.NO_OF_CATEGORIES_TO_SCRAPE:

        #print( f"\nLess than {cfg.NO_OF_CATEGORIES_TO_SCRAPE} categories ", f"with more than {cfg.MIN_BOOKS_PER_CATEGORY} books ","were found.")
        return

    # ---------------------------------
    # Display selected categories
    # ---------------------------------
    # for category, details in selected_categories.items():
        #print(f"{category} ", f"-> {details['book_count']} books")

    # ---------------------------------
    # Scrape selected categories
    # ---------------------------------
    all_books = []
    for category, details in selected_categories.items():
        #print( f"\nScraping category: ", f"{category}" )
        category_books = scrape_category(category,details["url"])
        all_books.extend(category_books)
        #print( f"    Books scraped: ", f"{len(category_books)}" )

    df = pd.DataFrame(all_books)
    output_folder = (
        cfg.PROJECT_ROOT
        / cfg.PIPELINES_OUTPUT_FOLDER
    )
    if not output_folder.exists():  output_folder.mkdir(parents=True,exist_ok=True)

    output_file = (output_folder/ "books_by_category_raw_data.csv")

    df.to_csv(output_file,index=False,encoding="utf-8" )

    return df, selected_categories, df.shape
