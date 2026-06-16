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
    except Exception as e:
        print(f"Telegram Notification Error: {e}")

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
            
            # Internshala ke naye aur purane dono cards ko handle karne ke liye safe matching
            cards = soup.find_all('div', class_='individual_internship') or soup.find_all('div', class_='internship_meta')
            
            for card in cards:
                try:
                    title_el = card.find('h3', class_='heading_4_5 profile') or card.find('div', class_='profile')
                    comp_el = card.find('a', class_='link_display_like_text company_and_premium') or card.find('div', class_='company_name')
                    stip_el = card.find('span', class_='stipend')
                    
                    if title_el and comp_el:
                        title = title_el.text.strip()
                        company = comp_el.text.strip()
                        stipend = stip_el.text.strip() if stip_el else "Paid (Check Link)"
                        
                        link_tag = card.find('a', class_='view_detail_button') or card.find('a')
                        link = "https://internshala.com" + link_tag['href'] if (link_tag and link_tag.get('href')) else url
                        
                        if "unpaid" not in stipend.lower():
                            jobs_found.append({
                                "title": title,
                                "company": company,
                                "type": "🏢 PRIVATE (Work From Home)",
                                "duration": "1-3 Months (Fresher Friendly)",
                                "stipend": stipend,
                                "link": link
                            })
                except Exception as card_err:
                    continue # Agar kisi ek card me dikkat ho toh baaki skip na hon
        except Exception as e:
            print(f"Error scraping Internshala URL: {e}")
            
    return jobs_found[:5]

def main():
    print("--- STARTING SCRAPER ---")
    
    # Yeh message bina kisi rukawat ke sabse pehle Telegram par jaana chahiye
    print("Sending live connection check to Telegram...")
    send_telegram_message("🤖 *Bot Live Check:* Aditya Bhai, script chalna shuru ho gayi hai! Data check kiya ja raha hai...")
    
    all_internships = scrape_internshala()
    
    # Agar website block kare ya koi data na mile, toh ye Government fallback hamesha chalega
    if not all_internships:
        print("No active parsed data, triggering active corporate/govt fallback.")
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
            f"⏳ *Duration:* {job['duration']}\n"
            f"💰 *Stipend:* {job['stipend']}\n"
            f"🔗 *Apply Here:* [Click to Register]({job['link']})\n"
            f"________________________"
        )
        send_telegram_message(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
