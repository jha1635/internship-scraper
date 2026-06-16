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
    # Hum response check karenge ki Telegram accept kar raha hai ya nahi
    response = requests.post(url, json=payload)
    print(f"Telegram API Response Status: {response.status_code}")
    print(f"Telegram API Response Body: {response.text}")

def scrape_internshala():
    jobs_found = []
    urls = [
        "https://internshala.com/internships/work-from-home-it-internships/",
        "https://internshala.com/internships/work-from-home-engineering-internships/"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='internship_meta')
            
            for card in cards:
                title_el = card.find('h3', class_='heading_4_5 profile')
                comp_el = card.find('a', class_='link_display_like_text company_and_premium')
                stip_el = card.find('span', class_='stipend')
                
                if title_el and comp_el and stip_el:
                    title = title_el.text.strip()
                    company = comp_el.text.strip()
                    stipend = stip_el.text.strip()
                    
                    link_tag = card.find('a', class_='view_detail_button')
                    link = "https://internshala.com" + link_tag['href'] if link_tag else url
                    
                    if "unpaid" not in stipend.lower():
                        jobs_found.append({
                            "title": title,
                            "company": company,
                            "type": "🏢 PRIVATE (Work From Home)",
                            "duration": "1-3 Months",
                            "stipend": stipend,
                            "link": link
                        })
        except Exception as e:
            print(f"Error scraping Internshala: {e}")
            
    return jobs_found[:5]

def main():
    print("--- STARTING SCRAPER ---")
    
    # 1. Sabse pehle ye line direct message bhejegi bina kisi condition ke
    print("Sending initial test message...")
    send_telegram_message(f"🚀 *Aditya Bhai Bot Live Ho Gaya Hai!*\n\nSystem successfully connect ho chuka hai. Abhi data nikalna shuru kar raha hu...")
    
    all_internships = scrape_internshala()
    
    # Fallback agar website block kar rahi ho toh manual government link bhej dega
    if not all_internships:
        print("Website parsing blocked or no match, sending corporate fallback.")
        all_internships.append({
            "title": "Govt Digital India / NIC Internship",
            "company": "Ministry of Electronics & IT (MeitY)",
            "type": "🏛️ GOVERNMENT (Online/Remote)",
            "duration": "1 - 3 Months",
            "stipend": "Paid (₹10,000/Month)",
            "link": "https://www.meity.gov.in/placement-and-internship"
        })
        
    for idx, job in enumerate(all_internships, 1):
        msg = (
            f"🔥 *New Internship Alert #{idx}*\n\n"
            f"📌 *Role:* {job['title']}\n"
            f"🏢 *Organization:* {job['company']}\n"
            f"🌐 *Category:* {job['type']}\n"
            f"⏳ *Duration:* {job['duration']} (Best for B.Tech/12th)\n"
            f"💰 *Stipend:* {job['stipend']}\n"
            f"🔗 *Apply Here:* [Click to Register]({job['link']})\n"
            f"________________________"
        )
        send_telegram_message(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
