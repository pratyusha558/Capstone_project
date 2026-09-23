# Books to Scrape — Web Scraping, Cleaning & SQLite Analysis

## Project Overview

This project scrapes book information from [Books to Scrape](https://books.toscrape.com/) using Python's `requests` and `BeautifulSoup` libraries.

The scraper collects books from the first **5 pages** of the "All Products" catalogue, resulting in **100 books**.

For each book, the following information is collected:

* `title`
* `price`
* `star_rating`
* `availability`
* `category`

The scraped data is then cleaned using Pandas and inserted into a SQLite database containing two related tables:

* `categories`
* `books`

SQL queries are then executed to demonstrate filtering, sorting, limiting, distinct values, range filtering, and table joins. The JOIN result is also reproduced using Pandas `merge()`.

---

## Technologies Used

* Python 3
* `requests`
* `BeautifulSoup4`
* `pandas`
* `sqlite3`
* SQLite

---

## Installation

Install the required Python libraries:

```bash
pip install requests beautifulsoup4 pandas
```

`sqlite3` is included with standard Python installations, so it does not need to be installed separately.

---

## How to Run

1. Open the project folder in VS Code.

2. Make sure the required packages are installed:

```bash
pip install requests beautifulsoup4 pandas
```

3. Run the Python script:

```bash
python your_python_file.py
```

The script performs the scraping, cleaning, database insertion, and SQL/Pandas analysis.

---

## Scraping Scope

The project uses the first five catalogue pages:

```text
https://books.toscrape.com/
https://books.toscrape.com/catalogue/page-2.html
https://books.toscrape.com/catalogue/page-3.html
https://books.toscrape.com/catalogue/page-4.html
https://books.toscrape.com/catalogue/page-5.html
```

Each page contains 20 books, giving a total of:

```text
5 pages × 20 books = 100 books
```

The individual book pages were also requested to extract the book category from the breadcrumb navigation.

---

## Parsing Decisions

### Title

The title was extracted from the book card using the `title` attribute of the book link.

### Price

The original scraped price is preserved in the `price` column.

A separate numeric `price_gbp` column was created for analysis.

Currency symbols or unexpected characters were removed by extracting the numeric portion of the price.

For example:

```text
£51.77 → 51.77
```

The cleaned `price_gbp` value is stored as a floating-point number.

### Star Rating

The website provides ratings as text:

```text
One
Two
Three
Four
Five
```

These values were converted into integers for database analysis:

```text
One   → 1
Two   → 2
Three → 3
Four  → 4
Five  → 5
```

The original `star_rating` text was retained in the cleaned dataset.

### Availability

The website provides availability as text such as:

```text
In stock
Out of stock
```

For the SQLite database, this was converted into an integer representation:

```text
In stock     → 1
Out of stock → 0
```

SQLite does not have a separate Boolean storage type, so integers were used for the Boolean-like field `in_stock`.

### Missing or Unparseable Numeric Values

If a numeric field could not be parsed, the invalid value was converted to `NaN`.

For numeric fields, missing values were handled using **median imputation** rather than allowing the pipeline to crash.

Median imputation was chosen because it provides a reasonable central value while being less affected by unusually high or low prices than the mean.

---

## SQLite Database Schema

### `categories`

```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
);
```

Each unique category is stored once.

### `books`

```sql
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER REFERENCES categories(category_id)
);
```

The `category_id` in the `books` table references the corresponding category in the `categories` table.

This creates a relationship between the two tables.

---

## SQL Analysis

The project executes SQL queries demonstrating:

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `DISTINCT`
* `BETWEEN`
* `JOIN`

The query strings and their outputs are saved in:

```text
sql_query_outputs.txt
```

---

## Pandas and SQL Comparison

At least two SQL query results are read into Pandas using:

```python
pd.read_sql()
```

The SQL JOIN result is independently reproduced using:

```python
pd.merge()
```

on the in-memory `books` and `categories` DataFrames.

The SQL JOIN result and Pandas merge result are compared using:

```python
df_sql_join.equals(df_merged)
```

The comparison confirms whether both approaches produce equivalent results.

---

## Project Files

Typical project files include:

```text
project/
│
├── your_python_file.py
├── books_data.csv
├── books_cleaned.csv
├── books.db
└── sql_query_outputs.txt
```

### File descriptions

* `your_python_file.py` — scraping, cleaning, database insertion, SQL queries, and Pandas analysis.
* `books_data.csv` — original scraped dataset.
* `books_cleaned.csv` — cleaned dataset used for analysis/database insertion.
* `books.db` — SQLite database containing the `books` and `categories` tables.
* `sql_query_outputs.txt` — SQL query strings and their corresponding outputs.

---

## Notes

The original scraped CSV is kept separately from the cleaned CSV so that the raw data is preserved and the cleaning process remains reproducible.
