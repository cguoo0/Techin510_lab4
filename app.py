import streamlit as st
import psycopg2
import os
import pandas as pd
from psycopg2 import sql, errors
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to connect to the database
def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        st.error("DATABASE_URL environment variable is not set")
        return None
    try:
        logger.info("Connecting to the database...")
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Connection successful")
        return conn
    except (Exception, errors.DatabaseError) as error:
        logger.error(f"Error connecting to the database: {error}")
        st.error(f"Error connecting to the database: {error}")
        return None

# Function to fetch books from the database
def fetch_books(query):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails
    try:
        cur = conn.cursor()
        logger.info("Executing query...")
        cur.execute(
            """
            SELECT title, price, stock, rating, description FROM books 
            WHERE title ILIKE %s OR description ILIKE %s
            ORDER BY rating DESC, price DESC
            """,
            ('%' + query + '%', '%' + query + '%',)
        )
        books = cur.fetchall()
        cur.close()
        conn.close()
        logger.info("Query successful")
        return pd.DataFrame(books, columns=['Title', 'Price', 'Stock', 'Rating', 'Description'])
    except (Exception, errors.DatabaseError) as error:
        logger.error(f"Error fetching books: {error}")
        st.error(f"Error fetching books: {error}")
        return pd.DataFrame()  # Return an empty DataFrame if query fails

# Streamlit UI components
def main():
    st.title("Book Search")
    query = st.text_input("Search books by name or description:")
    search_button = st.button('Search')

    if search_button and query:
        books_df = fetch_books(query)
        if not books_df.empty:
            st.write("Books found:")
            st.dataframe(books_df.style.format({'Price': "${:.2f}", 'Rating': "{:.1f}"}))
        else:
            st.write("No books found matching the search criteria.")

if __name__ == "__main__":
    main()
