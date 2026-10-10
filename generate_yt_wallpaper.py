import os
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

def get_date_string():
    # Lock timezone to IST (UTC+5:30)
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    
    # Calculate days left in the current month
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_left_month = days_in_month - now.day
    
    # Calculate days left in the year
    end_of_year = datetime(now.year, 12, 31, tzinfo=ist)
    days_left_year = (end_of_year.date() - now.date()).days
    
    return f"{days_left_month} | {days_left_year}"

def create_wallpaper():
    sub_count = get_subscriber_count()
    date_str = get_date_string()
    
    width, height = 1080, 2400

    # Pure OLED black
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        # Using a slightly smaller font for the date indicator so it stacks nicely
        font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except IOError:
        font_date = font_sub = ImageFont.load_default()

    center_x = width // 2
    
    # Stacked vertically right above the fingerprint sensor
    draw.text((center_x, 1800), date_str, fill=(255, 255, 255), font=font_date, anchor="mm")
    draw.text((center_x, 1875), sub_count, fill=(255, 255, 255), font=font_sub, anchor="mm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated. Counters: {date_str}, Sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
