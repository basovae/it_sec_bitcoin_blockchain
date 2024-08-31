from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

############################################
# Step 1: Static Scraping with BeautifulSoup
############################################

url = "https://www.walletexplorer.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# categories to scrape
wallet_categories = ['Exchanges', 'Pools', 'Services/others', 'Gambling']

wallet_links = {}

# extract the wallet links for each category
for category in wallet_categories:
    h3_tag = soup.find('h3', string=lambda text: category in text if text else False)
    if h3_tag:
        section = h3_tag.find_next('ul')
        links = section.find_all('a', href=True)
        wallet_links[category] = {link.text: link['href'] for link in links}
    else:
        print(f"Category {category} not found.")

############################################
# Step 2: Dynamic Scraping with Selenium
############################################

# ChromeDriver -- replace
driver_path = '/Users/ekaterinabasova/Downloads/chromedriver-mac-arm64/chromedriver'  # Update with your actual path

# directory where to save downloaded CSVs
base_download_dir = "/Users/ekaterinabasova/Documents/HU/Projects/itsec_blockchain_bitcoin_2024/2_collecting_scraped_addresses/scraper"  # Base directory

# Chrome options
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": base_download_dir}  # Base directory will be updated later
options.add_experimental_option("prefs", prefs)

# WebDriver Service
service = Service(executable_path=driver_path)

# ensuring all download directories exist
for category in wallet_links.keys():
    download_dir = os.path.join(base_download_dir, category.replace('/', '_'))  # Replace slashes in directory names
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

# visit each wallet's page, show addresses, and download the CSV
def download_wallet_csv(name, relative_url, download_dir):
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=service, options=options)
    
    wallet_url = f"https://www.walletexplorer.com{relative_url}"
    driver.get(wallet_url)

    try:
        # waiting for the <show wallet addresses> link and click it
        show_wallet_addresses_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "show wallet addresses"))
        )
        show_wallet_addresses_link.click()

        # waiting for the <download as CSV> link and clicking it
        download_csv_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Download as CSV"))
        )
        download_csv_link.click()

        # short delay to ensure the file has time to download
        time.sleep(8)

        print(f"Downloaded CSV for {name} in {download_dir}")

    except Exception as e:
        print(f"Failed to download CSV for {name}: {e}")
    
    driver.quit()

# iterating through each category
for category, wallets in wallet_links.items():
    category_download_dir = os.path.join(base_download_dir, category.replace('/', '_'))  # Ensure safe folder names
    for name, relative_url in wallets.items():
        download_wallet_csv(name, relative_url, category_download_dir)

print("All CSV files have been downloaded.")

