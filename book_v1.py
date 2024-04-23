import streamlit as st
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import psycopg2

load_dotenv()

# Ensure the environment variable is loaded
database_url = os.getenv('DATABASE_URL')
if database_url is None:
    raise ValueError("DATABASE_URL is not set in the environment variables")

# Establish the database connection
conn = psycopg2.connect(database_url)
c = conn.cursor()

# Create table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS books (
    name TEXT,
    price TEXT,
    rating TEXT,
    in_stock TEXT,
    description TEXT
)
''')
conn.commit()

# Mapping textual ratings to numeric values
ratings_mapping = {
    "Zero": 0,  
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def fetch_books(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def fetch_description(url):
    """ Fetch the product description from a book's detail page. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        description_block = soup.find('div', id='product_description')
        description_text = ''
        if description_block:
            next_sibling = description_block.find_next_sibling('p')
            description_text = next_sibling.text.strip() if next_sibling else "No description available"
        return description_text
    except requests.RequestException as e:
        print(f"Error fetching description: {e}")
        return "No description available"
    

def parse_books(soup, base_url):
    if soup is None:
        return

    books = []
    book_elements = soup.find_all('article', class_='product_pod')
    for book in book_elements:
        title = book.find('h3').find('a')['title']
        price_text = book.find('p', class_='price_color').text
        # Remove the 'Â£' symbol and convert to float
        price = float(price_text.replace('Â£', '').strip())
        rating_class = book.find('p', class_='star-rating')['class'][1]
        # Convert rating word to number using the mapping
        rating = ratings_mapping.get(rating_class, 0)
        in_stock = book.find('p', class_='instock availability').text.strip()

        # Getting the URL for each book's detail page
        relative_link = book.find('h3').find('a')['href']
        link = base_url + "catalogue/" + relative_link

        # Fetching the book's description
        description = fetch_description(link)

        books.append((title, price, rating, in_stock, description))

    # Insert all books at once
    c.executemany('INSERT INTO books (name, price, rating, in_stock, description) VALUES (%s, %s, %s, %s, %s)', books)
    conn.commit()

def scrape_books():
    base_url = "http://books.toscrape.com/catalogue/"

    # Start scraping from the first page of book listings
    first_page_url = base_url + "page-1.html"
    first_page = fetch_books(first_page_url)
    parse_books(first_page, base_url)

    # Initial setup to handle pagination
    next_button = first_page.find('li', class_='next') if first_page else None
    page_num = 2
    while next_button:
        next_page_url = base_url + "page-{}.html".format(page_num)  # Properly use format for each subsequent page
        next_page = fetch_books(next_page_url)
        parse_books(next_page, base_url)
        next_button = next_page.find('li', class_='next') if next_page else None
        page_num += 1

try:
    scrape_books()
finally:
    conn.close()
    print("Database connection closed.")

