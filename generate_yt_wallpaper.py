import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

def get_subscriber_count():
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    
    if not channel_id:
        print("Error: Missing YOUTUBE_CHANNEL_ID environment variable.")
        return "---"
        
    url = f"https://socialcounts.org/youtube-live-subscriber-count/{channel_id}"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Strategy 1: Extract from the meta description tag
        soup = BeautifulSoup(response.text, "html.parser")
        meta_desc = soup.find("meta", {"name": "description"})
        
        if meta_desc and "content" in meta_desc.attrs:
            desc_text = meta_desc["content"]
            # Looks for text like: "...presence with 1,234,567 subscribers..."
            match = re.search(r'with\s+([\d,]+)\s+subscribers', desc_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Strategy 2: Fallback to searching the raw HTML JSON/Next.js state payload
        match_json = re.search(r'"subscriberCount"\s*:\s*(\d+)', response.text)
        if match_json:
            return f"{int(match_json.group(1)):,}"
            
    except Exception as e:
        print("SocialCounts scraping error:", e)
        
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
    center_x = width // 2
    draw.text((center_x, 1875), sub_count, fill=(255, 255, 255), font=font, anchor="mm")

    img.save("daily_lockscreen.png")
    print(f"Wallpaper generated successfully with sub count: {sub_count}")

if __name__ == "__main__":
    create_wallpaper()
