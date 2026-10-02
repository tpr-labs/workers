python
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# Using GoodReturns as it has a historically stable structure for gold prices
URL = "https://www.goodreturns.in/gold-rates/bangalore.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
JSON_FILE = "bangalore_gold_prices.json"

def extract_prices(html_content):
    """
    Parses the HTML content to find 22K and 24K 1-gram gold prices.
    Returns a dictionary with the extracted prices.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    prices = {"22k": None, "24k": None}

    try:
        # Search all tables to locate the price grids
        tables = soup.find_all("table")
        for table in tables:
            text = table.get_text(separator=" ").lower()
            
            # Check if this table contains gold data
            if "1 gram" in text and ("22" in text or "24" in text):
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    row_text = " ".join([c.get_text(strip=True) for c in cols]).lower()
                    
                    # Target the 1-gram row specifically
                    if "1 gram" in row_text:
                        # Extract all numbers that look like valid INR prices (e.g., 6,500 or 72,000)
                        matches = re.findall(r'₹?\s*([\d,]+(?:\.\d{1,2})?)', row_text)
                        
                        for match in matches:
                            val = float(match.replace(',', ''))
                            # Sanity check: 1 gram gold is roughly between 4000 and 25000 INR
                            if 4000 < val < 25000:
                                if "22" in text and not prices["22k"]:
                                    prices["22k"] = val
                                elif "24" in text and not prices["24k"]:
                                    prices["24k"] = val
    except Exception as e:
        print(f"Error while parsing HTML table: {e}")

    return prices

def main():
    print(f"Fetching gold prices from {URL}...")
    
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch webpage: {e}")
        return

    # Extract the prices from the fetched HTML
    prices = extract_prices(response.text)

    if not prices["22k"] or not prices["24k"]:
        print("Warning: Could not find both 22K and 24K prices. Website structure may have changed.")
    else:
        print(f"Successfully Fetched -> 22K: ₹{prices['22k']}, 24K: ₹{prices['24k']}")

    data = []
    # If the JSON file already exists, read its contents first
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("Existing JSON file was corrupt. Starting fresh.")
            data = []

    # Create today's entry
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "date": today_date,
        "price_22k_inr": prices["22k"],
        "price_24k_inr": prices["24k"]
    }
    data.append(entry)

    # Write the updated array back to the JSON file
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print(f"Successfully saved data to {JSON_FILE}")

if __name__ == "__main__":
    main()