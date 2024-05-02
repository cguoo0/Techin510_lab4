import streamlit as st
import psycopg2
import os
import pandas as pd

# Function to connect to the database
def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Function to fetch books from the database
def fetch_books(query):
    conn = get_db_connection()
    cur = conn.cursor()
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
    return pd.DataFrame(books, columns=['Title', 'Price', 'Stock', 'Rating', 'Description'])

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
