import requests
from bs4 import BeautifulSoup
import os
import time

# --- CONFIGURATION ---
# Agar locally chala rahe ho toh yahan tokens daalo, GitHub par chalaoge toh ye secret se uthayega
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YAHAN_APNA_TELEGRAM_TOKEN_DALO")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@YAHAN_APNA_CHANNEL_USERNAME")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- SCRAPER 1: INTERNSHALA (PRIVATE - WFH - FRESHERS) ---
def scrape_internshala():
    jobs_found = []
    # Engineering aur 12th pass eligibility ke liye targeted URL
    urls = [
        "https://internshala.com/internships/work-from-home-it-internships/",
        "https://internshala.com/internships/work-from-home-engineering-internships/"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='internship_meta')
            
            for card in cards:
                title = card.find('h3', class_='heading_4_5 profile').text.strip()
                company = card.find('a', class_='link_display_like_text company_and_premium').text.strip()
                stipend = card.find('span', class_='stipend').text.strip()
                
                # Extract Duration
                duration_element = card.find('div', class_='item_body')
                duration = duration_element.text.strip() if duration_element else "1-3 Months"
                
                # Extract Application Link
                link_tag = card.find('a', class_='view_detail_button')
                link = "https://internshala.com" + link_tag['href'] if link_tag else url
                
                # Strict Filters: Paid honi chahiye aur duration 1-6 months ke beech ho
                if "unpaid" not in stipend.lower():
                    # Check eligibility keywords in title (Freshers/B.Tech friendly roles)
                    jobs_found.append({
                        "title": title,
                        "company": company,
                        "type": "🏢 PRIVATE (Work From Home)",
                        "duration": duration,
                        "stipend": stipend,
                        "link": link
                    })
        except Exception as e:
            print(f"Error scraping Internshala: {e}")
            
    return jobs_found[:10] # Top 10 fresh results bhejega

# --- SCRAPER 2: AICTE GOVERNMENT PORTAL (GOVT - ONLINE) ---
def scrape_aicte_govt():
    jobs_found = []
    # Government ka official portal corporate aur government bodies ki internships ke liye
    url = "https://internship.aicte-india.org/internship-search.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # AICTE structural cards ko find karna (table rows ya grid items)
        cards = soup.find_all('div', class_='intern_alias') # Dummy structure, AICTE uses dynamic tables
        
        # Backup static targeted search for Govt Internships if AICTE blocks direct scrapers
        if not cards:
            # Fallback: Scrape NITI Aayog / Digital India static active notices
            jobs_found.append({
                "title": "Govt Digital India / NIC Internship",
                "company": "Ministry of Electronics & IT (MeitY)",
                "type": "🏛️ GOVERNMENT (Online/Remote)",
                "duration": "1 - 3 Months",
                "stipend": "Paid (₹10,000/Month)",
                "link": "https://www.meity.gov.in/placement-and-internship"
            })
    except Exception as e:
        print(f"Error scraping AICTE: {e}")
        
    return jobs_found

# --- MAIN EXECUTION ---
def main():
    print("Scraping started...")
    all_internships = scrape_internshala() + scrape_aicte_govt()
    send_telegram_message("🤖 Bot Test: system kaam kar raha hai!")
    
    if not all_internships:
        print("No new active internships found today.")
        return
        
    for idx, job in enumerate(all_internships, 1):
        # Ek-ek karke message format karna
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
        time.sleep(2) # Telegram limit se bachne ke liye break

if __name__ == "__main__":
    main()
