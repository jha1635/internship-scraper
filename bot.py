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
                        stipend = stip_el.text.strip() if stip_el else "Paid (Check Link)"
                        
                        link_tag = card.find('a', class_='view_detail_button') or card.find('a')
                        link = "https://internshala.com" + link_tag['href'] if (link_tag and link_tag.get('href')) else url
                        
                        if "unpaid" not in stipend.lower():
                            jobs.append({
                                "title": title,
                                "company": company,
                                "type": "🏢 INTERNSHALA (Work From Home)",
                                "stipend": stipend,
                                "link": link
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"Internshala error: {e}")
    return jobs[:4]

def fetch_rss_jobs(url, category_name):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:3]:
                title = item.find('title').text.strip() if item.find('title') is not None else "Online Work"
                link = item.find('link').text.strip() if item.find('link') is not None else url
                jobs.append({
                    "title": title,
                    "company": "Verified Remote Platform",
                    "type": category_name,
                    "stipend": "Paid (Project Based)",
                    "link": link
                })
    except Exception as e:
        print(f"RSS error from {category_name}: {e}")
    return jobs

def main():
    print("--- STARTING MEGA COMBINED SCRAPER ---")
    
    send_telegram_message("🚀 *Mega Scanner Active:* Aditya Bhai, Internshala aur Global Remote networks dono ko ek sath connect kar diya gaya hai. List niche aa rahi hai...")

    all_jobs = []

    # 1. Internshala se technical/non-technical remote jobs uthao
    print("Scraping Internshala...")
    all_jobs.extend(scrape_internshala())

    # 2. Global RSS Feeds se har tarah ka ghar baithe wala kaam uthao
    sources = [
        {"url": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss", "name": "💻 DATA HANDLING & SUPPORT"},
        {"url": "https://weworkremotely.com/categories/remote-writing-jobs.rss", "name": "✍️ CONTENT WRITING & TRANSLATION"},
        {"url": "https://remoteok.com/remote-jobs.rss", "name": "🌐 GLOBAL REMOTE WORK (IT/Non-Tech)"}
    ]

    for source in sources:
        print(f"Scanning: {source['name']}")
        all_jobs.extend(fetch_rss_jobs(source['url'], source['name']))
        time.sleep(1)

    # 3. Government Fallback
    if not all_jobs:
        all_jobs.append({
            "title": "National Career Service (NCS) Portal",
            "company": "Ministry of Labour & Employment (Govt of India)",
            "type": "🏛️ GOVERNMENT (WFH/Online)",
            "stipend": "Paid Govt Scales",
            "link": "https://www.ncs.gov.in/"
        })

    # Top 10 mixed results ko channel par send karein
    for idx, job in enumerate(all_jobs[:10], 1):
        msg = (
            f"🔥 *Job/Internship Alert #{idx}*\n\n"
            f"📌 *Role:* {job['title']}\n"
            f"🏢 *Platform/Org:* {job['company']}\n"
            f"🌐 *Category:* {job['type']}\n"
            f"💰 *Stipend/Income:* {job['stipend']}\n"
            f"💻 *Setup:* 100% Ghar Baithe Online Kaam\n"
            f"🔗 *Apply Link:* [Click Here to Apply]({job['link']})\n"
            f"________________________"
        )
        send_telegram_message(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
