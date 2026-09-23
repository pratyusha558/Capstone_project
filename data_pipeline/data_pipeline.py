import sys
sys.stdout.reconfigure(encoding="utf-8")

import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin


books_data = []
for page in range(1,6):
    
    if page == 1:
      url = "https://books.toscrape.com/"
    else:
      url = f"https://books.toscrape.com/catalogue/page-{page}.html"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    #total books in webpage
    books = soup.find_all("article", class_="product_pod")

    # getting the price title,rating,category, availability
    for book in books:

      #title
      title = book.h3.a["title"]

      #price
      price = book.find("p", class_="price_color").text.strip()

      #rating
      rating = book.find("p", class_="star-rating")["class"][1]

      #availability
      availability = book.find(
          "p",
          class_="instock availability"
      ).text.strip()

      book_url = book.h3.a["href"]

      full_url = urljoin(url, book_url)

      book_response = requests.get(full_url)

      book_soup = BeautifulSoup(
          book_response.text,
          "html.parser"
      )

      breadcrumb = book_soup.find(
          "ul",
          class_="breadcrumb"
      )

      items = breadcrumb.find_all("li")

      category = items[2].text.strip()

      book_data = {
         "title": title,
          "price": price,
          "star_rating": rating,
          "availability": availability,
          "category":category
      }

      books_data.append(book_data)

'''coonverting scraped data into dataframe'''

import pandas as pd

df = pd.DataFrame(books_data)
df.to_csv("books_data.csv", index=False, encoding="utf-8")


import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

df = pd.read_csv("books_data.csv")

#extracting the number and coonverting into float
df["price_gbp"] = pd.to_numeric(
    df["price"]
    .str.extract(r'(\d+\.\d+)')[0],
    errors="coerce"
)

#placing the weired texts or number with the median value of price
median_price = df['price_gbp'].median()
df['price_gbp'] = df['price_gbp'].fillna(median_price)

#converting the text rating into numeric
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}
df["star_rating"] = df["star_rating"].map(rating_map)

#converting the gbp into inr pricing
df['price_inr'] = df['price_gbp']*105.50

#converting the availability statu into boolean
df["in_stock"] = df["availability"].str.contains("In stock").astype(int)

df.to_csv("books_cleaned.csv", index=False, encoding="utf-8")

#Database
import sqlite3

conn = sqlite3.connect("books.db")

cursor = conn.cursor()


#table1 :Categories
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY, 
    category_name TEXT UNIQUE
)
''')


#table2 :Books
cursor.execute('''
CREATE TABLE IF NOT EXISTS books (
  book_id INTEGER PRIMARY KEY, 
  title TEXT,
  price_gbp REAL, 
  price_inr REAL, 
  rating INTEGER, 
  in_stock INTEGER, 
  category_id INTEGER REFERENCES categories(category_id)
)
''')


conn.commit()
print("All tables are created")


#inserting the categories into category table 
categories = df["category"].unique()

for category in categories:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
        (category,)
    )

conn.commit()


#inserting the values into books table
for _, row in df.iterrows():

    cursor.execute(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (row["category"],)
    )

    category_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        row["star_rating"],
        row["in_stock"],
        category_id
    ))

conn.commit()

#query1
query1 = "SELECT title,price_gbp FROM books WHERE price_gbp >= 40"
cursor.execute(query1)

output1 = cursor.fetchall()

print("Query 1:")
print(query1)
print("Output:")
for row in output1:
    print(row)

#query 2
query2 = """
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
LIMIT 10;
"""

cursor.execute(query2)

output2 = cursor.fetchall()

print("Query 2:")
print(query2)
print("Output:")
for row in output2:
    print(row)

#query 3
query3 = """
SELECT DISTINCT category_name
FROM categories;
"""

cursor.execute(query3)

output3 = cursor.fetchall()

print("Query 3:")
print(query3)
print("Output:")
for row in output3:
    print(row)


#query4
query4 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 30;
"""

cursor.execute(query4)

output4 = cursor.fetchall()

print("Query 4:")
print(query4)
print("Output:")
for row in output4:
    print(row)

#query5 - JOIN
query5 = """
SELECT
    books.title,
    books.rating,
    categories.category_name
FROM books
JOIN categories
ON books.category_id = categories.category_id
ORDER BY books.rating DESC
LIMIT 10;
"""

cursor.execute(query5)

output5 = cursor.fetchall()

print("Query 5:")
print(query5)
print("Output:")
for row in output5:
    print(row)


#accessing query from pandas query1
query1 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp >= 40;
"""

df_query1 = pd.read_sql(query1, conn)

print(df_query1)

#accessing the query using pandas query2
query2 = """
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
LIMIT 10;
"""

df_query2 = pd.read_sql(query2, conn)

print(df_query2)

#pandas merge
df_books = pd.read_sql("SELECT * FROM books", conn)
df_categories = pd.read_sql("SELECT * FROM categories", conn)

df_merged = pd.merge(
    df_books,
    df_categories,
    on="category_id",
    how="inner"
)

df_merged = df_merged[
    ["title", "rating", "category_name"]
]

df_merged = (
    df_merged
    .sort_values(
        ["rating", "title"],
        ascending=[False, True]
    )
    .head(10)
    .reset_index(drop=True)
)


#coomparison of sql join and pandas merge
join_query = """
SELECT
    books.title,
    books.rating,
    categories.category_name
FROM books
INNER JOIN categories
    ON books.category_id = categories.category_id
ORDER BY books.rating DESC, books.title ASC
LIMIT 10;
"""

df_sql_join = pd.read_sql(join_query, conn)

df_sql_join = df_sql_join.reset_index(drop=True)

print("SQL:")
print(df_sql_join.to_string(index=False))

print("\nPANDAS:")
print(df_merged.to_string(index=False))

print(df_sql_join.equals(df_merged))





#saving the each query
with open("sql_query_outputs.txt", "w", encoding="utf-8") as f:

    f.write("QUERY 1\n")
    f.write(query1)
    f.write("\nOUTPUT:\n")
    for row in output1:
        f.write(str(row) + "\n")

    f.write("\nQUERY 2\n")
    f.write(query2)
    f.write("\nOUTPUT:\n")
    for row in output2:
        f.write(str(row) + "\n")

    f.write("\nQUERY 3\n")
    f.write(query3)
    f.write("\nOUTPUT:\n")
    for row in output3:
        f.write(str(row) + "\n")

    f.write("\nQUERY 4\n")
    f.write(query4)
    f.write("\nOUTPUT:\n")
    for row in output4:
        f.write(str(row) + "\n")

    f.write("\nQUERY 5 - JOIN\n")
    f.write(query5)
    f.write("\nOUTPUT:\n")
    for row in output5:
        f.write(str(row) + "\n")




