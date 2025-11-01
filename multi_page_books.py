
import csv
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

print("DEBUG: script started, flush=True")

BASE = "https://books.toscrape.com/"
START = urljoin(BASE, "catalogue/page-1.html")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
rating_map = {"One":"1","Two":"2","Three":"3","Four":"4","Five":"5"}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_page(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")
    for card in soup.select("article.product_pod"):
        title = card.h3.a["title"].strip()
        price = card.select_one("p.price_color").get_text(strip=True).replace("Â", "")
        availability = card.select_one("p.instock.availability").get_text(strip=True)
        rating_cls = card.select_one("p.star-rating")["class"]
        rating = next((rating_map[c] for c in rating_cls if c in rating_map), "0")
        url = urljoin(page_url, card.h3.a["href"])
        yield [title, price, rating, availability, url]

def next_page_url(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    nxt = soup.select_one("li.next a")
    return urljoin(page_url, nxt["href"]) if nxt else None

def crawl(pages: int | None = None):
    """Проходит по страницам каталога и собирает книги."""
    url = START
    collected = []
    seen = 0

    while url:
        html = fetch(url)
        collected.extend(parse_page(html, url))
        seen += 1
        print(f"DEBUG: страница {seen} собрана, всего {len(collected)} записей")

        if pages and seen >= pages:
            break

        url = next_page_url(html, url)
        time.sleep(0.5)

    return collected


if __name__ == "__main__":
    print("DEBUG: __main__ entered", flush=True)

    import os
    import argparse

    ap = argparse.ArgumentParser(description="Books to Scrape pagination parser")
    ap.add_argument("--pages", type=int, default=5, help="Сколько страниц собрать")
    ap.add_argument("--all", action="store_true", help="Собрать все страницы")
    ap.add_argument("--out", type=str, default="books_5pages.csv", help="Имя выходного CSV")
    args = ap.parse_args()

    rows = list(crawl(None if args.all else args.pages))
    out_path = os.path.abspath(args.out)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["title", "price", "rating", "availability", "url"])
        w.writerows(rows)

    print(f"Готово! Собрано записей: {len(rows)}", flush=True)
    print(f"Файл сохранён: {out_path}", flush=True)

























