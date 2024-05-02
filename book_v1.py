import os
import logging
import requests
from bs4 import BeautifulSoup
from psycopg2 import connect
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Constants
BASE_URL = "https://books.toscrape.com"

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Function to get a database connection
def get_db_connection():
    return connect(DATABASE_URL)

# Create or recreate the database table
def setup_database():
    with get_db_connection() as con:
        with con.cursor() as cur:
            # Drop the existing table if it exists
            cur.execute("DROP TABLE IF EXISTS books")
            # Create a new table
            cur.execute(
                """
                CREATE TABLE books
                (
                    title TEXT NOT NULL PRIMARY KEY,
                    price FLOAT NOT NULL,
                    stock INT NOT NULL,
                    rating NUMERIC NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        con.commit()

# Fetch all product links
def get_product_links():
    product_links = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/catalogue/page-{page}.html")
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        links = [x['href'] for x in soup.select("ol.row li article h3 a")]
        if not links:
            break
        product_links.extend(links)
        page += 1
    return product_links

# Scrape product data and insert into the database
def get_product(product_link):
    response = requests.get(f"{BASE_URL}/catalogue/{product_link}")
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.select_one(".product_main > h1").text
    price = float(soup.select_one(".price_color").text[2:])
    stock = int(soup.select_one(".instock.availability").text.strip().split('(')[1].split()[0])
    rating = rating_map[soup.select_one(".star-rating")['class'][1]]
    description = soup.select_one("#product_description + p")
    description = description.text if description else ""
    
    with get_db_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, price, stock, rating, description) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (title, price, stock, rating, description)
            )
        con.commit()

# Main function
if __name__ == "__main__":
    setup_database()
    product_links = get_product_links()
    for link in tqdm(product_links):
        try:
            get_product(link)
        except Exception as e:
            logging.error(f"Failed to process {link}: {str(e)}")
    print("Scraping completed")
