# Techin-510_Lab4
This Lab4 is a practice of using Scraper, Streamlit, and SQL database to fetch, store and display data.

# Overview
In this lab, I used scraper to fetch data, processing data and format data. Then i connect it with supabase to store the book information, including book title, rating, price, and description. Also i keep practice my skills in using streamlit to display chart,  filtering, arranging datas.

# Getting started
A PostgreSQL database
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# What's included
- A scraper file to fetch book information 
- A database to store and update book information
- A UI page which users are able to filter, search and ranking the book information.


# What I learned
- I have learned how to fetch data from exrernal sourcex. Like how to navigate web pages and extract relevant data, especially for descriptions.
- i have develop my skills in processing and formating the data obtained from scraping. like the cleaning of data, especially for price information.
- Connect my application to SQL through setting up the database, creating tables, and writing SQL queries to retrieve data.

# Questions
- How to fetch detail data like description
- My streamlit cannot successfully connect with github and always have problems when deploy. I may need more time to work on this and debug it.
- Now i have a books.db, but the format looks wired. how to foramt this into a table 
- how to setup db.py
