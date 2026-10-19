# Bookstore Intelligence Mission – Web Scraper

Scrapes the practice site https://books.toscrape.com/ with `requests` + `BeautifulSoup`,
builds a pandas DataFrame, saves `competitor_books.csv`, and answers the business questions.

## How it works
1. `scrape_page(url)` reads every `article.product_pod` on a page and extracts the title
   (`h3 > a[title]`), price (`p.price_color`), rating (`p.star-rating` class word converted to 1–5),
   availability (`p.availability`) and the product URL.
2. `scrape_catalogue(max_pages)` loops over `catalogue/page-N.html` and reuses the same function;
   it stops at a 404, so it can scrape the full catalogue.
3. `analyse(df)` answers the 7 questions, counts books per rating, draws a bar chart,
   and solves the £100 challenge exactly with a knapsack dynamic program.

## Run
```bash
pip install -r requirements.txt
python bookstore_scraper.py        # 5 pages (default)
python bookstore_scraper.py 3      # 3 pages
python bookstore_scraper.py all    # entire catalogue
```
Outputs: `competitor_books.csv`, `rating_counts.png`.
