import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

rating_map = {"One":"1","Two":"2","Three":"3","Four":"4","Five":"5"}

resp = requests.get(PAGE_URL, headers=HEADERS, timeout=20)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

rows = []
for card in soup.select("article.product_pod"):
    title = card.h3.a["title"].strip()
    price = card.select_one("p.price_color").get_text(strip=True).replace("Â", "")
    availability = card.select_one("p.instock.availability").get_text(strip=True)
    rating_cls = card.select_one("p.star-rating")["class"]
    rating = next((rating_map[c] for c in rating_cls if c in rating_map), "0")
    url = urljoin(PAGE_URL, card.h3.a["href"])
    rows.append([title, price, rating, availability, url])

with open("books_page1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["title","price","rating","availability","url"])
    w.writerows(rows)

print(f"Собрано записей: {len(rows)} (ожидаемо должно быть 20)")

