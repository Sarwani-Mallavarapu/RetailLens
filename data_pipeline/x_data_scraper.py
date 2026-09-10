from urllib.request import urlopen

from bs4 import BeautifulSoup as bs
import pandas as pd
from urllib.parse import urljoin

import config as cdr


BASE_URL = cdr.BASE_URL
NO_OF_PAGES = cdr.NO_OF_PAGES
output_folder = cdr.pipelines_output_folder

'''
outer html structure of the website is as follows:
<article class="product_pod">     
            <div class="image_container">                  
                    <a href="catalogue/a-light-in-the-attic_1000/index.html"><img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic" class="thumbnail"></a>              
            </div>    
                <p class="star-rating Three">
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                </p>       
            <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
            <div class="product_price">
        <p class="price_color">£51.77</p>
<p class="instock availability">
    <i class="icon-ok"></i>
        In stock
</p> 
    <form>
        <button type="submit" class="btn btn-primary btn-block" data-loading-text="Adding...">Add to basket</button>
    </form>              
            </div>
    </article>

'''



def get_product_info(product):
    name = product.select_one("h3 a")["title"]
    price = product.select_one("p.price_color").get_text(strip=True)
    availability = product.select_one(
        "p.instock.availability"
    ).get_text(strip=True)
    rating_classes = product.select_one("p.star-rating")["class"]
    rating = rating_classes[1]
    product_url = urljoin(
        BASE_URL,
        product.select_one("h3 a")["href"]
    )
    image_url = urljoin(
        BASE_URL,
        product.select_one("img")["src"]
    )
    return {
        "product_name": name,
        "price_gbp": price,
        "star_rating": rating,
        "availability": availability,
        "product_url": product_url,
        "image_url": image_url
    }

def get_url(page):
    if page == 1:
        return BASE_URL
    else:
        return urljoin(BASE_URL, f"catalogue/page-{page}.html")
def get_products_from_page(url):
    with urlopen(url, timeout=10) as response:
        page_html = response.read().decode("utf-8")
    soup = bs(page_html, "html.parser")
    products = soup.select("article.product_pod")
    return products


def scrape_books():
    all_books = []

    for page in range(1, NO_OF_PAGES + 1):
        url = get_url(page)
        print(f"Scraping page {page}: {url}")

        products = get_products_from_page(url)

        for product in products:
            product_info = get_product_info(product)

            all_books.append(product_info)

    df = pd.DataFrame(all_books)

    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / "raw_books_data.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print("\nScraping completed!")
    print(f"Total books scraped: {len(df)}")
    print(f"Saved to: {output_path}")

    return df
