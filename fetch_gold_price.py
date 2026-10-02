import json
import os
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

URL = "https://www.goodreturns.in/gold-rates/bangalore.html"
JSON_FILE = "bangalore_gold_prices.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def clean_price(text: str):
    # Extract only the main price before any daily change brackets like "(-33)"
    match = re.search(r'^[\s₹]*([\d,]+)', text)
    if match:
        try:
            val = float(match.group(1).replace(",", ""))
            if 4000 < val < 25000:
                return val
        except ValueError:
            pass
    return None

def fetch_gold_prices():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    found_prices = set()
    
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [col.get_text(strip=True).lower() for col in row.find_all(["td", "th"])]
            if not cols:
                continue
            
            # The website now uses just "1" in the Gram column
            if cols[0] in ["1", "1 gram", "1g", "1 gm"]:
                for col in cols[1:]:
                    val = clean_price(col)
                    if val:
                        found_prices.add(val)
    
    sorted_prices = sorted(list(found_prices))
    
    price_22k = None
    price_24k = None
    
    # 24K is the most expensive, 22K is the second most expensive (ignoring 18K)
    if len(sorted_prices) >= 2:
        price_24k = sorted_prices[-1]
        price_22k = sorted_prices[-2] 

    if not price_22k or not price_24k:
        print("Warning: Could not find both 22K and 24K prices.")
        print(f"Valid prices found in tables: {sorted_prices}")
    
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "price_22k_inr": price_22k,
        "price_24k_inr": price_24k
    }

def update_json_file(data: dict):
    records = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                if not isinstance(records, list):
                    records = [records]
        except (json.JSONDecodeError, IOError):
            records = []

    records.append(data)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print(f"Fetching gold prices from {URL}...")
    gold_data = fetch_gold_prices()
    update_json_file(gold_data)
    print(f"Successfully saved data to {JSON_FILE}")
