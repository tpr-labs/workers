import os
import requests
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
            return f"{int(sub_count):,}" # Formats number with commas (e.g., 1,234,567)
    except Exception as e:
        print("YouTube API error:", e)
        
    return "---"

def create_wallpaper():
    sub_count = get_subscriber_count()
    
    width, height = 1080, 2400

    # Pure OLED black
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Standard clean sans font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except IOError:
        font = ImageFont.load_default()

    # Centered horizontally, positioned right above the fingerprint sensor
    # Using Y=1875 to place it squarely in the middle of the previous two lines
    center_x = width // 2
    draw.text((center_x, 1875), sub_count, fill=(255, 255, 255), font=font, anchor="mm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated successfully with sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
