# Web scraping assignment: competitor bookstore (books.toscrape.com)
# Run: python bookstore_scraper.py 5   (or 3, or "all")

import re
import sys
import time
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_CSV = "competitor_books.csv"
BUDGET = 100

# ratings are stored as words in the html class, so convert them to numbers
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(text):
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group())


def parse_rating(tag):
    for name in tag.get("class", []):
        if name in RATING_WORDS:
            return RATING_WORDS[name]


# Mission 2: scrape one page
def scrape_page(url):
    response = requests.get(url, timeout=15)
    if response.status_code == 404:
        return None  # page does not exist
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        link = card.h3.a
        books.append({
            "Title": link["title"],
            "Price": parse_price(card.select_one("p.price_color").text),
            "Rating": parse_rating(card.select_one("p.star-rating")),
            "Availability": card.select_one("p.availability").get_text(strip=True),
            "URL": urljoin(url, link["href"]),
        })
    return books


# Mission 3: loop over pages
def scrape_catalogue(max_pages):
    all_books = []
    page = 1
    while max_pages is None or page <= max_pages:
        books = scrape_page(PAGE_URL.format(page))
        if books is None:
            break
        print("page", page, "-", len(books), "books")
        all_books.extend(books)
        page += 1
        time.sleep(0.5)
    return pd.DataFrame(all_books)


# Final challenge: best books for 100 pounds (knapsack, prices in pence)
def best_purchase(df, budget=BUDGET):
    prices = [int(round(p * 100)) for p in df["Price"]]
    ratings = df["Rating"].tolist()
    cap = int(round(budget * 100))

    best = np.zeros(cap + 1, dtype=np.int64)
    taken = np.zeros((len(prices), cap + 1), dtype=bool)
    for i, (p, r) in enumerate(zip(prices, ratings)):
        if p > cap:
            continue
        option = best[:cap + 1 - p] + r
        better = option > best[p:]
        taken[i, p:] = better
        best[p:] = np.where(better, option, best[p:])

    # smallest cost that reaches the best total, then walk back to find the books
    c = int(np.argmax(best == best[cap]))
    chosen = []
    for i in range(len(prices) - 1, -1, -1):
        if taken[i, c]:
            chosen.append(i)
            c -= prices[i]
    return df.iloc[sorted(chosen)]


def show(rows):
    return rows[["Title", "Price", "Rating"]].to_string(index=False)


# Mission 4: analysis
def analyse(df):
    print("\n1. Most expensive book:")
    print(show(df[df["Price"] == df["Price"].max()]))

    print("\n2. Cheapest book:")
    print(show(df[df["Price"] == df["Price"].min()]))

    print("\n3. Average price:", round(df["Price"].mean(), 2))

    five = df[df["Rating"] == 5]
    print("\n4. Number of 5-star books:", len(five))

    in_stock = df["Availability"].str.contains("In stock").mean() * 100
    print("\n5. Percentage in stock:", round(in_stock, 1))

    # many books have 5 stars, so cheaper books come first
    print("\n6. Top 5 highest rated books:")
    print(show(df.sort_values(["Rating", "Price"], ascending=[False, True]).head(5)))

    print("\n7. Cheapest 5-star book:")
    print(show(five[five["Price"] == five["Price"].min()]))

    # numbers for the business recommendation
    avg_all = df["Price"].mean()
    print("\nAverage price of all books:", round(avg_all, 2))
    print("Average price of 5-star books:", round(five["Price"].mean(), 2))
    print("5-star books cheaper than average:", (five["Price"] < avg_all).sum(), "of", len(five))
    print("Average price by rating:")
    print(df.groupby("Rating")["Price"].mean().round(2))

    # Bonus 3: books per rating
    counts = df["Rating"].value_counts().sort_index()
    print("\nBooks per rating:")
    print(counts)

    # CEO challenge
    picks = best_purchase(df)
    print("\nBooks to buy with 100 pounds:")
    print(show(picks))
    print("Total cost:", round(picks["Price"].sum(), 2))
    print("Total rating:", picks["Rating"].sum())

    # Bonus 4: bar chart
    import matplotlib.pyplot as plt
    counts.plot(kind="bar", color="steelblue", edgecolor="black")
    plt.title("Number of Books by Star Rating")
    plt.xlabel("Star rating")
    plt.ylabel("Number of books")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("rating_counts.png", dpi=150)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "5"
    max_pages = None if arg == "all" else int(arg)

    df = scrape_catalogue(max_pages)
    print("\nScraped", len(df), "books")
    print(df.head())

    df.to_csv(OUTPUT_CSV, index=False)
    print("Saved", OUTPUT_CSV)

    analyse(df)


if __name__ == "__main__":
    main()
