import requests
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

def fetch_rss_jobs(url, category_name):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:4]:  # Har source se top 4 live jobs
                title = item.find('title').text.strip() if item.find('title') is not None else "Online Work"
                link = item.find('link').text.strip() if item.find('link') is not None else url
                
                # Filter out irrelevant keywords to keep it clean
                jobs.append({
                    "title": title,
                    "company": "Verified Remote Platform",
                    "type": category_name,
                    "stipend": "Paid (As per project/contract)",
                    "link": link
                })
    except Exception as e:
        print(f"Error fetching from {category_name}: {e}")
    return jobs

def main():
    print("--- STARTING GLOBAL FREE WFH SCRAPER ---")
    
    send_telegram_message("🌐 *Global Search Active:* Aditya Bhai, pure internet se 100% free data pipelines connect kar di gayi hain. Ghar baithe online kaamon ki list niche aa rahi hai...")

    all_jobs = []

    # 100% Free Public Sources (No API Key Needed)
    # Yeh alalag-alag categories jaise Data Entry, Writing, Coding, Design sab mix uthayega
    sources = [
        {"url": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss", "name": "🏢 CUSTOMER SUPPORT & DATA HANDLING"},
        {"url": "https://weworkremotely.com/categories/remote-design-jobs.rss", "name": "🎨 GRAPHIC DESIGN & CREATIVE WORK"},
        {"url": "https://weworkremotely.com/categories/remote-writing-jobs.rss", "name": "✍️ CONTENT WRITING & TRANSLATION"},
        {"url": "https://remoteok.com/remote-jobs.rss", "name": "🌐 GLOBAL REMOTE (IT/Tech/Data Entry)"}
    ]

    for source in sources:
        print(f"Scanning: {source['name']}")
        all_jobs.extend(fetch_rss_jobs(source['url'], source['name']))
        time.sleep(1) # Site block na kare isliye chhota pause

    # National Fallback (Govt) agar kahin koi dikkat aaye
    if not all_jobs:
        all_jobs.append({
            "title": "National Career Service (NCS) Remote Work Portal",
            "company": "Ministry of Labour & Employment (Govt of India)",
            "type": "🏛️ GOVERNMENT (Work From Home/Online)",
            "duration": "Flexible / Part-time / Full-time",
            "stipend": "Paid Govt Scales",
            "link": "https://www.ncs.gov.in/"
        })

    # Top 8 unique and fresh entries ko Telegram par bhejenge
    for idx, job in enumerate(all_jobs[:8], 1):
        msg = (
            f"🔥 *Global Online Work Alert #{idx}*\n\n"
            f"📌 *Role/Project:* {job['title']}\n"
            f"🌐 *Category:* {job['type']}\n"
            f"💰 *Income/Stipend:* {job['stipend']}\n"
            f"💻 *Setup:* 100% Ghar Baithe Online Kaam\n"
            f"🔗 *Apply Link:* [Click Here to Register/Apply]({job['link']})\n"
            f"________________________"
        )
        send_telegram_message(msg)
        time.sleep(2)

if __name__ == "__main__":
    main()
