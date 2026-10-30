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
        # Loading Courier New font
        font_quote = ImageFont.truetype("cour.ttf", 32)
        font_data = ImageFont.truetype("cour.ttf", 36)  # Reduced from 45 for a smaller look
    except IOError:
        print("Warning: cour.ttf not found. Falling back to system monospace font.")
        try:
            font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 32)
            font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
        except IOError:
            font_quote = font_data = ImageFont.load_default()

    center_x = width // 2
    
    # 1. Draw Quote
    draw.text((center_x, 1720), quote_str, fill=(180, 180, 180), font=font_quote, anchor="mm")

    # 2. Reduced Wireframe Container Box Metrics (Tighter box)
    box_y_top = 1765
    box_y_bottom = 1840 # Reduced from 1855 (75px tall instead of 90px)
    cy = (box_y_top + box_y_bottom) // 2 
    
    box_width = 750 # Reduced from 900 (Much tighter horizontally)
    box_left = center_x - (box_width // 2)
    box_right = center_x + (box_width // 2)
    
    # Draw the main outer box and middle divider line
    box_color = (130, 130, 130)
    draw.rectangle([box_left, box_y_top, box_right, box_y_bottom], outline=box_color, width=2)
    draw.line([center_x, box_y_top, center_x, box_y_bottom], fill=box_color, width=2)

    # 3. Left Section: Calendar and Date (Slightly smaller, tighter spacing)
    left_center_x = box_left + (box_width // 4)
    
    bbox_date = draw.textbbox((0, 0), date_str, font=font_data)
    text_w_date = bbox_date[2] - bbox_date[0]
    icon_size = 28 # Reduced from 34
    pad = 12       # Reduced from 16
    total_w_date = icon_size + pad + text_w_date
    start_x_date = left_center_x - (total_w_date // 2)
    
    # Draw Calendar Vector Icon (Scaled down)
    ty_date = cy - (icon_size // 2)
    draw.rectangle([start_x_date, ty_date, start_x_date + icon_size, ty_date + icon_size], outline=(255, 255, 255), width=2)
    draw.line([start_x_date, ty_date + icon_size*0.35, start_x_date + icon_size, ty_date + icon_size*0.35], fill=(255, 255, 255), width=2)
    draw.line([start_x_date + icon_size*0.25, ty_date - 3, start_x_date + icon_size*0.25, ty_date + 3], fill=(255, 255, 255), width=2)
    draw.line([start_x_date + icon_size*0.75, ty_date - 3, start_x_date + icon_size*0.75, ty_date + 3], fill=(255, 255, 255), width=2)
    
    # Draw Date Text
    draw.text((start_x_date + icon_size + pad, cy), date_str, fill=(255, 255, 255), font=font_data, anchor="lm")

    # 4. Right Section: Play Button and Sub Count (Slightly smaller, tighter spacing)
    right_center_x = center_x + (box_width // 4)
    
    bbox_sub = draw.textbbox((0, 0), sub_count, font=font_data)
    text_w_sub = bbox_sub[2] - bbox_sub[0]
    total_w_sub = icon_size + pad + text_w_sub
    start_x_sub = right_center_x - (total_w_sub // 2)
    
    # Draw Play Vector Icon (Scaled down)
    ty_sub = cy - (icon_size // 2)
    draw.polygon([(start_x_sub, ty_sub), (start_x_sub, ty_sub + icon_size), (start_x_sub + int(icon_size*0.86), cy)], fill=(255, 255, 255))
    
    # Draw Sub Text
    draw.text((start_x_sub + icon_size + pad, cy), sub_count, fill=(255, 255, 255), font=font_data, anchor="lm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated. Quote: '{quote_str}', Counters: {date_str}, Sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
