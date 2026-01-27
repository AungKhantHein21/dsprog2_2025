import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
import pandas as pd

class TokyoDevScraperV2:
    def __init__(self, db_name="tokyodev_jobs.db"):
        self.base_url = "https://www.tokyodev.com/jobs"
        self.db_name = db_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._init_db()
        self.seen_urls = set() # To avoid duplicates

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                salary_raw TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                japanese_level TEXT,
                url TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def parse_salary(self, text):
        """
        Scans text for patterns like '¥8M' or '¥10M ~ ¥15M'
        Returns (8000000, 15000000)
        """
        # Look for numbers followed by 'M' (Millions)
        # matches will find ['8.5', '12'] from text "¥8.5M ~ ¥12M"
        matches = re.findall(r'¥(\d+(?:\.\d+)?)M', text)
        
        if len(matches) >= 2:
            min_val = float(matches[0]) * 1_000_000
            max_val = float(matches[1]) * 1_000_000
            return int(min_val), int(max_val)
        elif len(matches) == 1:
            val = float(matches[0]) * 1_000_000
            return int(val), int(val)
        return None, None

    def determine_japanese_level(self, text):
        """Scans text for Japanese requirements."""
        text = text.lower()
        if "no japanese" in text:
            return "None"
        elif "conversational" in text:
            return "Conversational"
        elif "business" in text:
            return "Business"
        elif "fluent" in text or "native" in text:
            return "Fluent"
        return "Unknown"

    def fetch_jobs(self, pages=2):
        print(f"--- STARTING SCRAPE (Pages 1-{pages}) ---")
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}?page={page}"
            print(f"Fetching: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # FIND ALL LINKS that go to a job detail page
                # This bypasses the need to know the 'div' class name
                job_links = soup.find_all('a', href=re.compile(r'/jobs/'))

                print(f"  -> Scanning {len(job_links)} links for data...")

                for link in job_links:
                    job_url = link['href']
                    
                    # Skip if we already processed this URL (deduplication)
                    if job_url in self.seen_urls:
                        continue
                    self.seen_urls.add(job_url)

                    # STRATEGY: Look at the text inside the link AND its parent container
                    # We climb up 3 levels to capture the whole "Card" text
                    # (Link -> Title -> Card Container)
                    try:
                        container = link.find_parent('div')
                        if not container:
                            continue
                            
                        full_text = container.get_text(" ", strip=True)
                        
                        # Check if this container actually has salary info
                        if "¥" not in full_text or "M" not in full_text:
                            # Try going one level higher just in case
                            parent = container.parent
                            if parent:
                                full_text = parent.get_text(" ", strip=True)
                        
                        # Now parse the text found
                        min_sal, max_sal = self.parse_salary(full_text)
                        
                        if min_sal:
                            title = link.get_text(strip=True)
                            # If title is empty (sometimes the link wraps an image), try finding an H2 nearby
                            if not title:
                                h2 = container.find('h2')
                                if h2: title = h2.get_text(strip=True)
                            
                            japanese = self.determine_japanese_level(full_text)
                            
                            # Clean the raw text for the DB
                            salary_str = f"¥{min_sal/1000000}M"
                            
                            self._save_to_db(title, salary_str, min_sal, max_sal, japanese, job_url)
                            print(f"    Saved: {title[:20]}... | {japanese} | ¥{min_sal:,}")
                            
                    except Exception as e:
                        # Skip bad links silently
                        continue

                time.sleep(2) # Be polite

            except Exception as e:
                print(f"Error on page {page}: {e}")

    def _save_to_db(self, title, raw_sal, min_sal, max_sal, japanese_level, url):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (title, salary_raw, salary_min, salary_max, japanese_level, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, raw_sal, min_sal, max_sal, japanese_level, url))
        conn.commit()
        conn.close()

# --- EXECUTION ---
if __name__ == "__main__":
    scraper = TokyoDevScraperV2()
    scraper.fetch_jobs(pages=3)