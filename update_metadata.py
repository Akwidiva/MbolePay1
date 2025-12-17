import os
import json
import glob

def update_metadata_files():
    metadata_dir = "cloud_storage/metadata"
    files = glob.glob(os.path.join(metadata_dir, "*.json"))

    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Update uploading_node
            if "uploading_node" in data and data["uploading_node"] == "BasicVM":
                data["uploading_node"] = "Node1"

            # Update visible_to_nodes
            if "visible_to_nodes" in data:
                updated_nodes = []
                for node in data["visible_to_nodes"]:
                    if node == "BasicVM":
                        updated_nodes.append("Node1")
                    elif node.startswith("VM"):
                        # Extract number and convert to Node
                        num = node[2:]  # Remove "VM" prefix
                        updated_nodes.append(f"Node{num}")
                    else:
                        updated_nodes.append(node)
                data["visible_to_nodes"] = updated_nodes

            # Write back
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Updated {file_path}")

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

if __name__ == "__main__":
    update_metadata_files()