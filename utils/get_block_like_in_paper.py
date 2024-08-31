import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os

LATEST_BLOCK_API_URL = "https://chain.api.btc.com/v3/block/latest"
BLOCK_DETAILS_API_URL = "https://chain.api.btc.com/v3/block/{block_height}/tx?page={page}&pagesize={pagesize}"
PAGESIZE = 50 
MAX_WORKERS = 10 

def fetch_latest_block_height():
    """
    Fetch the latest block height from the BTC.com API.
    """
    try:
        response = requests.get(LATEST_BLOCK_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['data']['height']
    except requests.RequestException as e:
        print(f"Error fetching the latest block height: {e}")
        return None

def fetch_page(block_height, page, pagesize=PAGESIZE):
    """
    Fetch a single page of transactions for a given block height.
    """
    url = BLOCK_DETAILS_API_URL.format(block_height=block_height, page=page, pagesize=pagesize)
    try:
        response = requests.get(url, timeout=10) 
        response.raise_for_status() 
        return response.json()
    except requests.HTTPError as e:
        if response.status_code == 404:
            print(f"Data for block {block_height} not found on page {page}. Skipping.")
        else:
            print(f"HTTP error fetching page {page} of block {block_height}: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error fetching page {page} of block {block_height}: {e}")
        return None

def fetch_block_transactions_concurrently(block_height, total_pages):
    """
    Fetch all transaction pages for a given block height concurrently.
    """
    all_transactions = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_page, block_height, page) for page in range(1, total_pages + 1)]
        
        for future in as_completed(futures):
            result = future.result()
            if result and "data" in result and "list" in result["data"]:
                all_transactions.extend(result["data"]["list"])
    
    return all_transactions

def save_block_to_cache(block_height, transactions):
    """
    Save fetched transactions to a cache file.
    """
    os.makedirs('blocks', exist_ok=True)
    cache_file = f'blocks/block_{block_height}.json'
    with open(cache_file, 'w') as f:
        json.dump(transactions, f, indent=2)
    print(f"Saved block {block_height} data to {cache_file}")

def main():
    # Step 1: Fetch the latest block height
    latest_block_height = fetch_latest_block_height()
    if not latest_block_height:
        print("Failed to fetch the latest block height. Exiting.")
        return

    print(f"Latest block height is {latest_block_height}.")

    # Step 2: Fetch the 10 most recent blocks
    num_blocks = 200
    for block_height in range(latest_block_height, latest_block_height - num_blocks, -1):
        print(f"Fetching data for block height: {block_height}")

        # Fetching the first page to determine the total number of pages
        first_page_data = fetch_page(block_height, 1)
        if not first_page_data or "data" not in first_page_data:
            print(f"Failed to fetch data for block height: {block_height}. Skipping.")
            continue
        
        total_pages = first_page_data['data']['page_total']
        print(f"Block {block_height} has {total_pages} pages of transactions.")

        # Fetch all transactions concurrently for the current block
        transactions = fetch_block_transactions_concurrently(block_height, total_pages)

        if transactions:
            print(f"Fetched {len(transactions)} transactions for block {block_height}")
            save_block_to_cache(block_height, transactions)
        else:
            print(f"Failed to fetch transactions for block {block_height}")

if __name__ == "__main__":
    main()
