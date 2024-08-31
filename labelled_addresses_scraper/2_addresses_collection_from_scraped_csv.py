import os
import pandas as pd

scraper_folder = 'scraper'

def extract_addresses(folder_path, address_column='address'):
    addresses = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            print(f"Reading file: {file_path}")

            try:
                # skip first row and read the second row as headers
                df = pd.read_csv(file_path, skiprows=1)

                # checking if the specified address column exists
                if address_column in df.columns:
                    df = df[[address_column]].copy()  # keeping only the address column
                    addresses.append(df)
                    print(f"Extracted {len(df)} addresses from {file_name}.")
                else:
                    print(f"No '{address_column}' column found in {file_name}. Column names found: {df.columns}")

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return pd.concat(addresses, ignore_index=True) if addresses else pd.DataFrame()

def process_labeled_folders(scraper_folder):
    for folder_name in os.listdir(scraper_folder):
        folder_path = os.path.join(scraper_folder, folder_name)
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}...")

            addresses_df = extract_addresses(folder_path, address_column='address')

            if not addresses_df.empty:
                output_file = f"{folder_name}_addresses.csv"
                addresses_df.to_csv(output_file, index=False)
                print(f"Saved addresses to {output_file}")
            else:
                print(f"No addresses found in {folder_name}.")

process_labeled_folders(scraper_folder)

