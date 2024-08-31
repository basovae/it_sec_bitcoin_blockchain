import os
import pandas as pd
from collections import defaultdict

def load_labeled_addresses(csv_folder, labels):
    """
    Load labeled addresses from CSV files for different business sectors.

    Args:
    - csv_folder (str): Directory path containing labeled address CSV files.
    - labels (list): List of labels corresponding to the business sectors.

    Returns:
    - dict: Dictionary with labels as keys and sets of addresses as values.
    """
    labeled_addresses = defaultdict(set)

    for label in labels:
        file_path = os.path.join(csv_folder, f'{label}_addresses.csv')
        df_addresses = pd.read_csv(file_path)
        labeled_addresses[label].update(df_addresses['address'].tolist())

    return labeled_addresses

def map_transactions_to_labels(transactions_csv, labeled_addresses):
    """
    Map transactions to labels based on the associated addresses.

    Args:
    - transactions_csv (str): File path of the CSV containing transaction-address data.
    - labeled_addresses (dict): Dictionary with labels as keys and sets of addresses as values.

    Returns:
    - pd.DataFrame: DataFrame with transactions and their corresponding labels.
    """
    df_transactions = pd.read_csv(transactions_csv)

    labeled_transactions = []

    for index, row in df_transactions.iterrows():
        txid = row['Transaction ID']
        address = row['Address']
        label = map_address_to_label(address, labeled_addresses)
        if label:
            labeled_transactions.append((txid, label))

    df_labeled_transactions = pd.DataFrame(labeled_transactions, columns=['tx_hash', 'Label'])
    return df_labeled_transactions

def map_address_to_label(address, labeled_addresses):
    """
    Maps a single address to its respective label based on labeled addresses data.

    Args:
    - address (str): The address to be labeled.
    - labeled_addresses (dict): A dictionary mapping labels to sets of addresses.

    Returns:
    - str or None: The label if found, else None.
    """
    for label, addresses in labeled_addresses.items():
        if address in addresses:
            return label
    return None

def save_labeled_transactions(df, output_file):
    """
    Saves the labeled transactions DataFrame to a CSV file.

    Args:
    - df (pd.DataFrame): DataFrame with transactions and their corresponding labels.
    - output_file (str): Output CSV file path.
    """
    df.to_csv(output_file, index=False)
    print(f"Labeled transactions saved to {output_file}")

if __name__ == "__main__":
    csv_folder = "2_collecting_scraped_addresses"
    
    labels = ['Exchanges', 'Pools', 'Services_others', 'Gambling']

    transactions_csv = "1_bitcoin_data_fetch_and_graph_creation/txid_addresses.csv"

    output_file = "labeled_transactions.csv"

    labeled_addresses = load_labeled_addresses(csv_folder, labels)

    df_labeled_transactions = map_transactions_to_labels(transactions_csv, labeled_addresses)

    save_labeled_transactions(df_labeled_transactions, output_file)
