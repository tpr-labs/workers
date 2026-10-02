import json
import os
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

URL = "https://www.goodreturns.in/gold-rates/bangalore.html"
JSON_FILE = "bangalore_gold_prices.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    )
}

def clean_price(text: str):
    """Extracts only the numbers from the table cell."""
    match = re.search(r'[\d,]+', text)
    if match:
        return float(match.group(0).replace(",", ""))
    return None

def fetch_gold_prices():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    price_22k = None
    price_24k = None

    # Resilient Strategy: Scan all tables across the entire page for '1 gram'
    found_prices = set()
    
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [col.text.strip().lower() for col in row.find_all(["td", "th"])]
            # If the row mentions '1 gram', parse the price next to it
            if len(cols) >= 2 and "1 gram" in cols[0]:
                val = clean_price(cols[1])
                if val:
                    found_prices.add(val)
    
    # 22K gold is always cheaper than 24K. 
    # Sort the unique prices we found and assign the two highest values.
    sorted_prices = sorted(list(found_prices))
    
    if len(sorted_prices) >= 2:
        price_22k = sorted_prices[0]
        price_24k = sorted_prices[-1] 

    if not price_22k or not price_24k:
        print("Warning: Could not find both 22K and 24K prices. Website structure may have changed.")
    
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
