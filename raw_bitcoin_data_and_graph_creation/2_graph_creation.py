import json
import os
import graph_tool.all as gt
from tqdm import tqdm
from decimal import Decimal
import traceback
import dill as pickle
from collections import defaultdict

reverse_map = defaultdict(dict)

def satoshi_to_btc(satoshi):
    return float(Decimal(satoshi) / Decimal(100000000))

def add_graph_properties(graph):
    # transaction node properties
    for prop in ["tx_hash", "tx_inputs_count", "tx_inputs_value", "tx_outputs_count", 
                 "tx_outputs_value", "tx_block_height", "tx_block_time", "tx_fee", "tx_size"]:
        graph.vp[prop] = graph.new_vertex_property("string" if prop == "tx_hash" else "double")
    
    # address node properties
    for prop in ["address", "prev_type", "next_type"]:
        graph.vp[prop] = graph.new_vertex_property("string")
    
    # Eege properties
    graph.ep["value"] = graph.new_edge_property("double")
    graph.ep["time"] = graph.new_edge_property("int")
    graph.ep["tx_type"] = graph.new_edge_property("string")


def add_tx_node(graph, **kwargs):
    tx_node = graph.add_vertex()
    for key, value in kwargs.items():
        graph.vp[f"tx_{key}"][tx_node] = value
    reverse_map["transaction_dict"][kwargs["hash"]] = graph.vertex_index[tx_node]
    return tx_node

def add_address_node(graph, address, node_type):
    if address not in reverse_map["account_dict"]:
        ads_node = graph.add_vertex()
        reverse_map["account_dict"][address] = graph.vertex_index[ads_node]
        graph.vp["address"][ads_node] = address
        graph.vp[f"{node_type}_type"][ads_node] = "unknown"
    else:
        ads_node = graph.vertex(reverse_map["account_dict"][address])
    return ads_node

def add_edge(graph, source, target, value, time):
    try:
        edge = graph.add_edge(source, target)
        graph.ep["value"][edge] = value
        graph.ep["time"][edge] = time
        return edge
    except Exception as e:
        print(f"Error adding edge: {e}")
        return None

def process_transaction(graph, tx, block_height, block_time):
    try:
        tx_hash = tx["txid"]
        
        tx_node = add_tx_node(
            graph,
            hash=tx_hash,
            inputs_count= len(tx["vin"]),
            inputs_value= sum(satoshi_to_btc(vin.get("value", 0)) for vin in tx["vin"] if "value" in vin),
            outputs_count=len(tx["vout"]),
            outputs_value=sum(satoshi_to_btc(vout["value"]) for vout in tx["vout"]),
            block_height=block_height,
            block_time=block_time,
            fee=satoshi_to_btc(tx.get("fee", 0)),
            size=tx["size"]
        )

        for vin in tx["vin"]:
            if "coinbase" not in vin:
                input_address = vin.get("address", "unknown")
                input_node = add_address_node(graph, input_address, "prev")
                edge = add_edge(graph, input_node, tx_node, satoshi_to_btc(vin.get("value", 0)), block_time)
                if edge:
                    graph.ep["tx_type"][edge] = "standard"

        for vout in tx["vout"]:
            if vout["scriptPubKey"].get("type") == "nulldata":
                op_return_node = add_address_node(graph, "OP_RETURN", "next")
                edge = add_edge(graph, tx_node, op_return_node, 0, block_time)
                if edge:
                    graph.ep["tx_type"][edge] = "op_return"
            else:
                output_address = vout["scriptPubKey"].get("address", "unknown")
                output_node = add_address_node(graph, output_address, "next")
                edge = add_edge(graph, tx_node, output_node, satoshi_to_btc(vout["value"]), block_time)
                if edge:
                    script_type = vout["scriptPubKey"].get("type", "unknown")
                    graph.ep["tx_type"][edge] = "complex" if script_type not in ["pubkey", "pubkeyhash", "scripthash", "witness_v0_keyhash", "witness_v0_scripthash"] else "standard"

    except Exception as e:
        print(f"Error processing transaction {tx.get('txid', 'unknown')}: {e}")
        traceback.print_exc()

def process_block(graph, block_data):
    try:
        block_height = block_data["height"]
        block_time = block_data["time"]

        for tx in block_data["tx"]:
            process_transaction(graph, tx, block_height, block_time)
    except Exception as e:
        print(f"Error processing block at height {block_data.get('height', 'unknown')}: {e}")
        traceback.print_exc()

def traverse_folder(graph, folder_path):
    for filename in tqdm(os.listdir(folder_path)):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as json_file:
                    try:
                        block_data = json.load(json_file)
                        process_block(graph, block_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                traceback.print_exc()

if __name__ == '__main__':
    graph = gt.Graph(directed=True)
    add_graph_properties(graph)

    folder_path = os.path.join(os.getcwd().replace('\\', '/'), 'blocks')
    traverse_folder(graph, folder_path)

    with open("revmap.pkl", "wb") as f:
        pickle.dump(dict(reverse_map), f)

    graph.save("BitcoinGraph.gt")

    print("Graph generation complete. Files saved as 'BitcoinGraph.gt' and 'revmap.pkl'.")
