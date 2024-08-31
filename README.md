# Bitcoin Blockchain 2024 - Lawful Analytics and Privacy

**Type:** Seminar Paper

**Authors:** Ekaterina Basova

**Supervisor:** Prof. Dr. Ben Fabian, Prof. Dr. Tatiana Ermakova

![results](/graph.png)

## Table of Content

- [Summary](#summary)
- [Setup](#Setup)
- [Reproducing results](#Reproducing-results)
- [Results](#Results)
- [Project structure](#Project-structure)

## Summary

Exploring Bitcoin transactions (retrieved with Quicknode RCP) now includes labelled wallets from walletexplorer.com.

## Setup

Python version - 3.12.2

1. Clone this repository

2. Create an virtual environment and activate it

```bash
python -m venv transf_mv_forecast
source transf_mv_forecast/bin/activate
```

3. Install requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Reproducing results

The analysis consists of the main `Notebook.ipynb` where the results of the data retrieval are visualised and analysed. A big inspiration for the codes used in this repository was the [BABD: A Bitcoin Address Behaviour Dataset for Pattern Analysis](https://github.com/Y-Xiang-hub/Bitcoin-Address-Behavior-Analysis/tree/main) repository related to a paper with a similar research topic.

To get the necessary data after cloning the repository, first fetch the bitcoin block data by moving to the `raw_bitcoin_data_and_graph_creation` folder.

The `1_get_block_data.py` file connects to the Quicknode API and fetches raw block data in the form of JSON files into the `/blocks` folder. The `rpc_url` field should be replaced with an active, valid Quicknode API connector. In the `/utils` folder under the name `get_block_like_in_paper.py` is another more universal approach to retrieving raw bitcoin data, copied from the [BABDs paper repository](https://github.com/Y-Xiang-hub/Bitcoin-Address-Behavior-Analysis/tree/main) repository.

Once the data has been downloaded into the `/blocks` folder, the `2_graph_creation.py` script will use it to create a graph of the data. This will create `BitcoinGraph.gt` and `revmap.pkl` files which will be used in notebook to analyse the graph structure.

The third script in the `3_transact_and_address_matching.py` folder creates a list of transactions and their corresponding recipient addresses. It is called `txid_addresses.csv' and will be useful for labelled addresses that match the transaction id at the evaluation stage of the analysis.

The second folder called `labelled_addresses_scraper` contains two scripts. The first, `1_walletexplorer_scraper.py`, dynamically scrapes [WalletExplorer.com](https://www.walletexplorer.com/), which provides a summarised collection of publicly known bitcoin addresses assigned to corresponding companies and fields of activity (e.g. exchange or gambling). The results are stored in the `/scraper` folder and then called by `2_addresses_collection_from_scraped_csv.py`, which collects the different addresses by business area into corresponding csv files.

The `transaction_labelling.py` script brings together the pre-processed csvs from the scraper and transaction address mapping to create a transaction label mapping, which is used at the end of the notebook to see which labels fall into which clusters.

Due to github restrictions, all the data files can't be uploaded to the remote repository, so they can be found in the Google Drive at the following [link](https://drive.google.com/drive/folders/1cEgDN0RkTph7EUQG5RCn0yEUgV_sXQnB?usp=sharing)

## Results

![results](/PCA_clusters.png)

![results](/cluster_results.png)

The study examines Bitcoin

## Project structure

```bash
├── labelled_addresses_scraper                      -- contains scraper related files
    ├── scraper                                     -- raw scraping results
        ├── Gambling
        ├── Services_others
        ├── Pools
        └── Exchange
    ├── 1_walletexplorer_scraper.py                 -- WalletExplorer scraper scrip
    ├── 2_addresses_collection_from_scraped_csv.py  -- address assignment according to area of operation
    ├── Exchanges_addresses.csv                     -- result of address mapping for Exchange business area
    ├── Gambling_addresses.csv                      -- result of address mapping for Gambling business area
    ├── Pools_addresses.csv                         -- result of address mapping for Pools business area
    └── Services_others_addresses.csv               -- result of address mapping for Services
├── raw_bitcoin_data_and_graph_creation             -- Bitcoin raw data related files and scripts
    ├── blocks
        ├── block_857927.json                       -- raw blockwise bitcon data
        ├── ....
        └── block_858927.json
    ├── 1_get_block_data.py                         -- block download via Quicknode
    ├── 2_graph_creation.py                         -- graph structure from raw blocks
    ├── BitcoinGraph.gt                             -- extracted graph file
    ├── revmap.pkl                                  -- grapph supporting file
    └── txid_addresses.csv                          -- transaction receiving address mapping
├── utils
    └── get_block_like_in_paper.py              -- data retrieval similar to BADS paper
├── extracted_transaction_features.csv              -- transaction features extracted from graph in the Notebook
├── labeled_transactions.csv                        -- scraper-transaction mapping result
├── Notebook.ipynb                                  -- notebook file
├── README.md
├── requirements.txt                                -- required libraries
└── transaction_labelling.py                        --
```
