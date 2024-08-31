import json
import os
import glob
import csv

def extract_txid_addresses(data):
    """
    Extracts transaction IDs (txid) and associated output addresses from raw JSON data.

    Args:
    - data (dict): The raw JSON data containing blockchain transaction information.

    Returns:
    - list of tuples: A list of (txid, address) tuples.
    """
    txid_addresses = []

    for tx in data.get('tx', []):
        txid = tx['txid']
        for vout in tx.get('vout', []):
            address = vout['scriptPubKey'].get('address')
            if address:
                txid_addresses.append((txid, address))

    return txid_addresses

def process_all_json_files(directory):
    """
    Processes all JSON files in the given directory and extracts txid-address pairs.

    Args:
    - directory (str): The directory containing JSON files.

    Returns:
    - list of tuples: A consolidated list of (txid, address) tuples from all files.
    """
    all_txid_addresses = []

    # all JSON files in the directory
    json_files = glob.glob(os.path.join(directory, "*.json"))

    for json_file in json_files:
        with open(json_file, 'r') as f:
            try:
                raw_data = json.load(f)
                # transaction IDs and addresses from each file
                txid_addresses = extract_txid_addresses(raw_data)
                all_txid_addresses.extend(txid_addresses)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {json_file}: {e}")
            except Exception as e:
                print(f"Error processing file {json_file}: {e}")

    return all_txid_addresses

def save_to_csv(data, output_file):
    """
    Saves the extracted txid-address pairs to a CSV file.

    Args:
    - data (list of tuples): The extracted txid-address pairs.
    - output_file (str): The output CSV file path.
    """
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Transaction ID', 'Address'])  # Write header
        writer.writerows(data)

def main():
    directory = 'blocks'
    all_txid_addresses = process_all_json_files(directory)
    output_file = 'txid_addresses.csv'
    save_to_csv(all_txid_addresses, output_file)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
