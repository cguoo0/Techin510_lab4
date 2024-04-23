import streamlit as st
import pandas as pd
import sqlalchemy

# Establishing connection to the database
# Update the connection string according to your database configuration
def setup_database():
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    engine = sqlalchemy.create_engine(DATABASE_URL)

def fetch_data(search_query="", five_star_only=False):
    query = f"""
    SELECT * FROM books
    WHERE book_name ILIKE '%%{search_query}%%'
    """
    if five_star_only:
        query += " AND rating = 5"
    return pd.read_sql(query, engine)

def main():
    st.title('Book Information Dashboard')

    # Search bar
    search_query = st.text_input("Search by book name")

    # Filter for five-star rating
    five_star_only = st.checkbox("Show only five-star books")

    # Fetching data from the database
    if st.button('Search'):
        df = fetch_data(search_query, five_star_only)
        if not df.empty:
            st.write(df)
        else:
            st.write("No books found")

if __name__ == "__main__":
    main()
