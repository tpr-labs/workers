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
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    sub_count = get_subscriber_count()
    date_str = get_date_string(now)
    quote_str = get_daily_quote(now)
    
    width, height = 1080, 2400
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        # Looking for the uploaded Courier New font
        font_quote = ImageFont.truetype("cour.ttf", 35)
        font_date = ImageFont.truetype("cour.ttf", 45)
        font_sub = ImageFont.truetype("cour.ttf", 60)
    except IOError:
        print("Warning: cour.ttf not found. Falling back to system monospace font.")
        try:
            font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 35)
            font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 45)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 60)
        except IOError:
            font_quote = font_date = font_sub = ImageFont.load_default()

    center_x = width // 2
    
    # 1. Draw Quote (Centered as normal)
    draw.text((center_x, 1720), quote_str, fill=(180, 180, 180), font=font_quote, anchor="mm")

    # 2. Draw Date with Calendar Icon
    bbox_date = draw.textbbox((0, 0), date_str, font=font_date)
    text_w_date = bbox_date[2] - bbox_date[0]
    icon_size_date = 35
    pad_date = 20
    total_w_date = icon_size_date + pad_date + text_w_date
    start_x_date = center_x - (total_w_date // 2)
    cy_date = 1800
    
    # Draw vector calendar icon
    ty_date = cy_date - (icon_size_date // 2)
    draw.rectangle([start_x_date, ty_date, start_x_date + icon_size_date, ty_date + icon_size_date], outline=(255, 255, 255), width=3)
    draw.line([start_x_date, ty_date + icon_size_date*0.35, start_x_date + icon_size_date, ty_date + icon_size_date*0.35], fill=(255, 255, 255), width=3)
    draw.line([start_x_date + icon_size_date*0.25, ty_date - 4, start_x_date + icon_size_date*0.25, ty_date + 4], fill=(255, 255, 255), width=3)
    draw.line([start_x_date + icon_size_date*0.75, ty_date - 4, start_x_date + icon_size_date*0.75, ty_date + 4], fill=(255, 255, 255), width=3)
    
    # Draw date text aligned to the right of the icon
    draw.text((start_x_date + icon_size_date + pad_date, cy_date), date_str, fill=(255, 255, 255), font=font_date, anchor="lm")

    # 3. Draw Subscriber Count with Play Icon
    bbox_sub = draw.textbbox((0, 0), sub_count, font=font_sub)
    text_w_sub = bbox_sub[2] - bbox_sub[0]
    icon_size_sub = 42
    pad_sub = 20
    total_w_sub = icon_size_sub + pad_sub + text_w_sub
    start_x_sub = center_x - (total_w_sub // 2)
    cy_sub = 1880
    
    # Draw vector play icon
    ty_sub = cy_sub - (icon_size_sub // 2)
    draw.polygon([(start_x_sub, ty_sub), (start_x_sub, ty_sub + icon_size_sub), (start_x_sub + icon_size_sub*0.86, cy_sub)], fill=(255, 255, 255))
    
    # Draw sub text aligned to the right of the icon
    draw.text((start_x_sub + icon_size_sub + pad_sub, cy_sub), sub_count, fill=(255, 255, 255), font=font_sub, anchor="lm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated. Quote: '{quote_str}', Counters: {date_str}, Sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
