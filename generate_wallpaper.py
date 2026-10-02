import os
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# URLs
GOLD_URL = "https://www.goodreturns.in/gold-rates/bangalore.html"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current_weather=true"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

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
                        match = re.search(r'^[\s₹]*([\d,]+)', col)
                        if match:
                            try:
                                val = float(match.group(1).replace(",", ""))
                                if 4000 < val < 25000:
                                    found_prices.add(val)
                            except ValueError:
                                pass
        
        sorted_prices = sorted(list(found_prices))
        if len(sorted_prices) >= 2:
            return sorted_prices[-2], sorted_prices[-1]  # 22K and 24K
    except Exception as e:
        print("Gold fetch error:", e)
    return None, None

def get_weather():
    try:
        response = requests.get(WEATHER_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        return current.get("temperature", "--"), current.get("windspeed", "--")
    except Exception as e:
        print("Weather fetch error:", e)
    return "--", "--"

def create_wallpaper():
    price_22k, price_24k = get_gold_prices()
    temp, wind = get_weather()
    
    # 1080x2400 is the standard aspect ratio for modern smartphones
    width, height = 1080, 2400
    
    # Create dark minimalist background (very dark grey-blue)
    img = Image.new('RGB', (width, height), color=(15, 18, 25))
    draw = ImageDraw.Draw(img)
    
    # We use Ubuntu's default DejaVu fonts installed via GitHub Actions
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except IOError:
        font_title = font_medium = font_small = ImageFont.load_default()

    # Get formatted date
    date_str = datetime.now().strftime("%A\n%d %B %Y")
    
    # Format display strings
    gold_22_str = f"22K: ₹{price_22k or '---'}"
    gold_24_str = f"24K: ₹{price_24k or '---'}"
    weather_str = f"{temp}°C   |   Wind: {wind} km/h"
    
    # Draw elements (adjusted for visual spacing on a lockscreen)
    draw.text((100, 350), "Dashboard", fill=(255, 255, 255), font=font_title)
    draw.text((100, 480), date_str, fill=(150, 160, 175), font=font_medium)
    
    draw.text((100, 850), "Gold (1g)", fill=(255, 215, 0), font=font_medium)
    draw.text((100, 950), gold_22_str, fill=(230, 230, 230), font=font_small)
    draw.text((100, 1020), gold_24_str, fill=(230, 230, 230), font=font_small)
    
    draw.text((100, 1250), "Bangalore Weather", fill=(100, 200, 255), font=font_medium)
    draw.text((100, 1350), weather_str, fill=(230, 230, 230), font=font_small)
    
    img.save("daily_lockscreen.png")
    print("Wallpaper generated successfully as daily_lockscreen.png")

if __name__ == "__main__":
    create_wallpaper()
