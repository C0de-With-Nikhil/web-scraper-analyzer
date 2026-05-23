import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

# 1. The CORRECT, live URL for Ahmedabad properties
url = "https://www.99acres.com/property-in-ahmedabad-ffid"

print("Booting up an undetected Chrome browser...")

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=147)

try:
    print(f"Navigating to {url}...")
    driver.get(url)
    
    print("Waiting 10 seconds for the page to fully load...")
    time.sleep(10) 
    
    # 1. Grab the raw HTML from the browser
    html_source = driver.page_source
    
    # 2. SAVE IT LOCALLY (The Sandbox Technique)
    print("Saving the webpage HTML to your local folder...")
    with open("99acres_raw.html", "w", encoding="utf-8") as file:
        file.write(html_source)
        
    print("\n✅ SUCCESS! The webpage has been downloaded.")
    
finally:
    print("Closing browser...")
    driver.quit()
    print("Done! You now have a file named '99acres_raw.html'.")