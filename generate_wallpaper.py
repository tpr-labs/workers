import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Data Sources
GOLD_URL = "https://www.goodreturns.in/gold-rates/bangalore.html"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current_weather=true"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def clean_price(text: str):
    match = re.search(r'^[\s₹]*([\d,]+)', text)
    if match:
        try:
            val = float(match.group(1).replace(",", ""))
            if 4000 < val < 25000:
                return val
        except ValueError:
            pass
    return None

def get_gold_prices():
    try:
        response = requests.get(GOLD_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        found_prices = set()
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cols = [col.get_text(strip=True).lower() for col in row.find_all(["td", "th"])]
                if not cols:
                    continue
                if cols[0] in ["1", "1 gram", "1g", "1 gm"]:
                    for col in cols[1:]:
                        val = clean_price(col)
                        if val:
                            found_prices.add(val)

        sorted_prices = sorted(list(found_prices))
        if len(sorted_prices) >= 2:
            return sorted_prices[-2], sorted_prices[-1]  # 22K, 24K
    except Exception as e:
        print("Gold fetch error:", e)
    return None, None

def get_weather():
    try:
        response = requests.get(WEATHER_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        temp = current.get("temperature", "--")
        wind = current.get("windspeed", "--")
        return temp, wind
    except Exception as e:
        print("Weather fetch error:", e)
    return "--", "--"

def create_wallpaper():
    price_22k, price_24k = get_gold_prices()
    temp, wind = get_weather()

    width, height = 1080, 2400

    # Pure OLED black
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Standard clean sans font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Format text strings
    gold_str = f"22K: ₹{int(price_22k) if price_22k else '---'}   |   24K: ₹{int(price_24k) if price_24k else '---'}"
    weather_str = f"BLR: {temp}°C   |   Wind: {wind} km/h"

    # Centered horizontally, positioned above the fingerprint sensor
    center_x = width // 2
    draw.text((center_x, 1840), gold_str, fill=(255, 255, 255), font=font, anchor="mm")
    draw.text((center_x, 1910), weather_str, fill=(255, 255, 255), font=font, anchor="mm")

    img.save("daily_lockscreen.png")
    print("Wallpaper generated successfully as daily_lockscreen.png")

if __name__ == "__main__":
    create_wallpaper()
