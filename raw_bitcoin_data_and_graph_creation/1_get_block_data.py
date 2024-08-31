import requests
import json
import csv
from collections import defaultdict
import logging
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import os
import networkx as nx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# QuickNode RPC URL
rpc_url = "--"

def rpc_call(method, params=[]):
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "curltest",
        "method": method,
        "params": params
    })
    response = requests.post(rpc_url, headers=headers, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()['result']

def get_block_from_cache(height):
    cache_file = f'blocks/block_{height}.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_block_to_cache(block, height):
    os.makedirs('blocks', exist_ok=True)
    cache_file = f'blocks/block_{height}.json'
    with open(cache_file, 'w') as f:
        json.dump(block, f, indent=2)

def fetch_blocks(num_blocks=10):
    logging.info(f"Fetching the last {num_blocks} blocks")
    current_height = rpc_call("getblockcount")
    blocks = []
    for height in range(current_height, current_height - num_blocks, -1):
        cached_block = get_block_from_cache(height)
        if cached_block:
            logging.info(f"Using cached data for block at height {height}")
            blocks.append(cached_block)
        else:
            logging.info(f"Fetching block at height {height}")
            block_hash = rpc_call("getblockhash", [height])
            block = rpc_call("getblock", [block_hash, 2])
            save_block_to_cache(block, height)
            blocks.append(block)
    return blocks
blocks = fetch_blocks(1000)
