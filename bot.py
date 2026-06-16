import requests
from bs4 import BeautifulSoup
import os
import time

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram API Status: {response.status_code}")
        print(f"Telegram Response Body: {response.text}") # Yeh line batayegi ki asal me kya galti hai!
    except Exception as e:
        print(f"Telegram Notification Error: {e}")

def main():
    print("--- STARTING DEBUG SCRAPER ---")
    
    # Yeh check karne ke liye ki variables sahi se load hue ya nahi
    print(f"Using Chat ID: {TELEGRAM_CHAT_ID}")
    if TELEGRAM_TOKEN:
        print(f"Token Loaded Successfully (Length: {len(TELEGRAM_TOKEN)})")
    else:
        print("CRITICAL ERROR: TELEGRAM_TOKEN IS EMPTY!")

    print("Sending live connection check to Telegram...")
    send_telegram_message("🤖 *Bot Live Check:* Aditya Bhai, script chal rahi hai!")

if __name__ == "__main__":
    main()
