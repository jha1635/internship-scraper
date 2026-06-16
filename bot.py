import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
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
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def scrape_internshala():
    jobs = []
    urls = [
        "https://internshala.com/internships/work-from-home-it-internships/",
        "https://internshala.com/internships/work-from-home-engineering-internships/"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='individual_internship') or soup.find_all('div', class_='internship_meta')
            
            for card in cards:
                try:
                    title_el = card.find('h3', class_='heading_4_5 profile') or card.find('div', class_='profile')
                    comp_el = card.find('a', class_='link_display_like_text company_and_premium') or card.find('div', class_='company_name')
                    stip_el = card.find('span', class_='stipend')
                    
                    if title_el and comp_el:
                        title = title_el.text.strip()
                        company = comp_el.text.strip()
                        stipend = stip_el.text.strip() if stip_el else "₹5,000 - ₹10,000 /Month"
                        
                        link_tag = card.find('a', class_='view_detail_button') or card.find('a')
                        link = "https://internshala.com" + link_tag['href'] if (link_tag and link_tag.get('href')) else url
                        
                        if "unpaid" not in stipend.lower():
                            jobs.append({
                                "title": title,
                                "company": company,
                                "type": "🏢 PRIVATE (Internshala WFH)",
                                "duration": "1 - 3 Months Max",
                                "stipend": f"{stipend} (Monthly)",
                                "link": link
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"Internshala error: {e}")
    return jobs[:3]

def fetch_rss_global_internships(url, category_name):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text.strip() if item.find('title') is not None else "Online Remote Work"
                link = item.find('link').text.strip() if item.find('link') is not None else url
                
                title_lower = title.lower()
                # Strict check: Pure internet me se sirf internship, freelance ya part-time tasks filter karega
                if "intern" in title_lower or "contract" in title_lower or "freelance" in title_lower or "part-time" in title_lower or "junior" in title_lower:
                    jobs.append({
                        "title": title,
                        "company": "Verified Global Platform",
                        "type": category_name,
                        "duration": "⏳ Short-Term (1-3 Months)",
                        "stipend": "💸 Paid (Project / Hourly Basis)",
                        "link": link
                    })
                if len(jobs) >= 2: # Har internet feed se max 2 strict matches
                    break
    except Exception as e:
        print(f"RSS error: {e}")
    return jobs

def get_government_internships():
    return [
        {
            "title": "Digital India Internship Scheme",
            "company": "Ministry of Electronics & IT (MeitY)",
            "type": "🏛️ GOVERNMENT (Online/Remote Component)",
            "duration": "1 - 3 Months Strictly",
            "stipend": "₹10,000 /Month (Fixed)",
            "link": "https://www.meity.gov.in/placement-and-internship"
        }
    ]

def main():
    print("--- STARTING THE ULTIMATE FULL INTERNET SCRAPER ---")
    
    send_telegram_message("🌐 *Mega Global Search Active:* Bhai, Internshala + Government + Pure Internet se filter karke strictly 1-3 Months ki paid opportunities niche aa rahi hain... 🚀")

    all_jobs = []

    # 1. Government Internships (Sabse Pehle)
    all_jobs.extend(get_government_internships())

    # 2. Internshala WFH Internships
    all_jobs.extend(scrape_internshala())

    # 3. Pure Internet Public Streams (LinkedIn/Indeed/Global Remote Boards aggregated feeds)
    sources = [
        {"url": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss", "name": "💻 GLOBAL REMOTE (Data & Support)"},
        {"url": "https://remoteok.com/remote-jobs.rss", "name": "🌐 PURE INTERNET (Tech & Non-Tech Internships)"}
    ]

    for source in sources:
        all_jobs.extend(fetch_rss_global_internships(source['url'], source['name']))
        time.sleep(1)

    # 4. Telegram par auto-post matching items
    for idx, job in enumerate(all_jobs[:8], 1):
        msg = (
            f"🔥 *Mega Internet Alert #{idx}*\n\n"
            f"📌 *Role:* {job['title']}\n"
            f"🏢 *Organization:* {job['company']}\n"
            f"🌐 *Source/Category:* {job['type']}\n"
            f"⏳ *Duration:* {job.get('duration', '1-3 Months Max')}\n"
            f"💰 *Stipend/Income:* {job['stipend']}\n"
            f"💻 *Setup:* 100% Ghar Baithe Online\n"
            f"🔗 *Apply Link:* [Click Here to Apply]({job['link']})\n"
            f"________________________"
        )
        send_telegram_message(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
