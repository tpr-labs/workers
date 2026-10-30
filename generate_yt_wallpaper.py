import os
import json
import requests
import calendar
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

def get_date_string(now):
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_left_month = days_in_month - now.day
    
    end_of_year = datetime(now.year, 12, 31, tzinfo=now.tzinfo)
    days_left_year = (end_of_year.date() - now.date()).days
    
    return f"{days_left_month} | {days_left_year}"

def get_daily_quote(now):
    try:
        with open("quotes.json", "r") as f:
            quotes = json.load(f)
        
        if not quotes:
            return ""
            
        day_of_year = now.timetuple().tm_yday
        quote_index = (day_of_year - 1) % len(quotes)
        return quotes[quote_index]
        
    except FileNotFoundError:
        print("quotes.json not found.")
        return ""
    except Exception as e:
        print("Error reading quotes:", e)
        return ""

def create_wallpaper():
    # Lock timezone to IST (UTC+5:30)
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    sub_count = get_subscriber_count()
    date_str = get_date_string(now)
    quote_str = get_daily_quote(now)
    
    width, height = 1080, 2400
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load custom Matrix / Nothing font if available, else fallback to Monospace
    try:
        font_quote = ImageFont.truetype("matrix.ttf", 35)
        font_date = ImageFont.truetype("matrix.ttf", 45)
        font_sub = ImageFont.truetype("matrix.ttf", 60)
    except IOError:
        try:
            # Fallback to Ubuntu's default monospace terminal font
            font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 30)
            font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 40)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 55)
        except IOError:
            font_quote = font_date = font_sub = ImageFont.load_default()

    center_x = width // 2
    
    # Vertically stacked layout - adjusted spacing for larger matrix fonts
    draw.text((center_x, 1720), quote_str, fill=(180, 180, 180), font=font_quote, anchor="mm")
    draw.text((center_x, 1800), date_str, fill=(255, 255, 255), font=font_date, anchor="mm")
    draw.text((center_x, 1880), sub_count, fill=(255, 255, 255), font=font_sub, anchor="mm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated. Quote: '{quote_str}', Counters: {date_str}, Sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
