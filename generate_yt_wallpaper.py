import os
import requests
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

def get_subscriber_count():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    
    if not api_key or not channel_id:
        print("Error: Missing API Key or Channel ID environment variables.")
        return "---"
        
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            sub_count = data["items"][0]["statistics"]["subscriberCount"]
            return f"{int(sub_count):,}"
    except Exception as e:
        print("YouTube API error:", e)
        
    return "---"

def get_date_string():
    # Lock timezone to IST (UTC+5:30)
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    
    current_day = now.day
    end_of_year = datetime(now.year, 12, 31, tzinfo=ist)
    days_left = (end_of_year.date() - now.date()).days
    
    return f"{current_day} | {days_left}"

def get_sun_and_moon():
    # Fetch Sunrise and Sunset for Bangalore
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&daily=sunrise,sunset&timezone=Asia%2FKolkata"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract time strings (e.g., "2026-10-02T06:12" -> "06:12")
        sunrise = data['daily']['sunrise'][0].split("T")[1]
        sunset = data['daily']['sunset'][0].split("T")[1]
    except Exception as e:
        print("Weather API error:", e)
        sunrise, sunset = "--:--", "--:--"
        
    # Calculate current Moon Phase mathematically
    now = datetime.now(timezone.utc)
    new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc) # A known historical new moon
    phase = ((now - new_moon).total_seconds() / 86400.0) % 29.530588 / 29.530588
    
    if phase < 0.03 or phase >= 0.97: moon = "🌑"
    elif phase < 0.22: moon = "🌒"
    elif phase < 0.28: moon = "🌓"
    elif phase < 0.47: moon = "🌔"
    elif phase < 0.53: moon = "🌕"
    elif phase < 0.72: moon = "🌖"
    elif phase < 0.78: moon = "🌗"
    else: moon = "🌘"
    
    return f"↑ {sunrise}   ↓ {sunset}   |   {moon}"

def create_wallpaper():
    sub_count = get_subscriber_count()
    date_str = get_date_string()
    sun_moon_str = get_sun_and_moon()
    
    width, height = 1080, 2400

    # Pure OLED black
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        # Using a slightly smaller font for the sun/moon sub-line
        font_sun = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except IOError:
        font_date = font_sun = font_sub = ImageFont.load_default()

    center_x = width // 2
    
    # Stacked vertically right above the fingerprint sensor
    draw.text((center_x, 1770), date_str, fill=(255, 255, 255), font=font_date, anchor="mm")
    draw.text((center_x, 1830), sun_moon_str, fill=(200, 200, 200), font=font_sun, anchor="mm")
    draw.text((center_x, 1900), sub_count, fill=(255, 255, 255), font=font_sub, anchor="mm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated. Date: {date_str}, Sun/Moon: {sun_moon_str}, Sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
