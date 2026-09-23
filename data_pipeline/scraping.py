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