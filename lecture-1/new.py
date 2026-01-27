import requests
from bs4 import BeautifulSoup
import re

# --- CONFIGURATION ---
URL = "https://www.tokyodev.com/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def run_diagnostic():
    print(f"--- DIAGNOSTIC: CONNECTING TO {URL} ---")
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        print(f"Status Code: {response.status_code}") # Should be 200
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect. {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # TEST 1: IS THE CONTENT THERE?
    # We check if the word "Engineer" or "Developer" appears in the HTML.
    page_text = soup.get_text()
    if "Engineer" in page_text or "Developer" in page_text:
        print("✅ Success: Page content seems to be loaded.")
    else:
        print("❌ FAIL: The page looks empty. It might be blocked or require JavaScript.")

    # TEST 2: CAN WE FIND JOB LINKS?
    # Instead of looking for specific classes like 'job-list-item' (which change),
    # let's look for any link that looks like a job post (e.g. href="/jobs/...")
    job_links = soup.find_all('a', href=re.compile(r'/jobs/'))
    
    print(f"Found {len(job_links)} potential job links.")

    if len(job_links) > 0:
        print("--> WE CAN FIX THIS! The jobs are there, we just need to target these links.")
        print(f"Example Link: {job_links[0]['href']}")
        # Check the parent of the link to see what class we should target
        parent = job_links[0].find_parent('div')
        if parent:
            print(f"Parent Container Class: {parent.get('class')}")
    else:
        print("--> PROBLEM: No job links found.")

    # TEST 3: SAVE THE DEBUG FILE
    with open("tokyodev_debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\n📄 I have saved 'tokyodev_debug.html'.")
    print("Please open this file in your browser. Do you see a list of jobs? or a CAPTCHA?")

if __name__ == "__main__":
    run_diagnostic()