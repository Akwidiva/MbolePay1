# CloudSim - Distributed Cloud Storage Simulation

A Python-based simulation of a distributed cloud storage system, mimicking real-world services like Google Drive.

## Features

- **Distributed Nodes**: Run multiple storage nodes as separate processes
- **Central Cloud Management**: Cloud server coordinates operations
- **File Upload/Download**: Store and retrieve files across nodes
- **Inter-Node Transfers**: Replicate files between nodes with verification
- **Heartbeat Monitoring**: Nodes send health status to cloud
- **Resource Simulation**: CPU, memory, storage, and bandwidth modeling
- **File Location Tracking**: Know which nodes store each file
- **Real-time Statistics**: Monitor system health and usage

## Architecture

- **Cloud Server** (`cloud_server.py`): Central coordinator
- **Node Clients** (`node_client.py`): Individual storage nodes
- **Core Classes**: Cloud, StorageVirtualNetwork, StorageVirtualNode

## Running the Simulation

### 1. Start the Cloud Server
```bash
python cloud_server.py
```
This starts the cloud server on localhost:12345.

### 2. Start Node Clients
In separate terminals, run:
```bash
python node_client.py
```
Enter node details when prompted (ID, CPU, Memory, Storage, Bandwidth).

### 3. Cloud Server Commands
- `register_user <user_id>`: Register a new user
- `connect <node1> <node2> <bandwidth>`: Connect nodes with bandwidth
- `stats`: Show cloud statistics
- `nodes`: List node statuses
- `quit`: Shutdown server

### 4. Node Client Commands
- `upload <user_id> <file_name> <file_size>`: Upload a file
- `download <user_id> <file_id>`: Download a file
- `transfer <file_id> <to_node>`: Transfer file to another node
- `list_files <user_id>`: List user's files and their storage locations
- `quit`: Disconnect node

## Example Usage

1. Start cloud server in terminal 1
2. Start node1 in terminal 2 (ID: node1, CPU:4, Mem:16, Stor:500, BW:1000)
3. Start node2 in terminal 3 (ID: node2, CPU:8, Mem:32, Stor:1000, BW:2000)
4. In cloud server: `register_user alice`
5. In cloud server: `connect node1 node2 1000`
6. In node1: `upload alice document.pdf 104857600` (100MB)
7. In node1: `list_files alice` (shows uploaded file and file_id)
8. In node1: `transfer <file_id> node2` (replicates file to node2)
9. In node2: `list_files alice` (verifies file is now on both nodes)
10. In node2: `download alice <file_id>` (tests download from replicated location)

## Verification

After transfer, check:
- `list_files <user>` shows `'stored_on': ['node1', 'node2']`
- `stats` in cloud server shows file distribution
- Download works from any node storing the file

## Real-World Comparison

This simulation models:
- **Google Drive**: User file storage, sharing, sync
- **Distributed Storage**: Files spread across multiple servers
- **Load Balancing**: Automatic node selection for storage
- **Replication**: Data redundancy across nodes
- **Monitoring**: Health checks and resource tracking
- **Network Simulation**: Realistic transfer delays and bandwidth limits

## Troubleshooting

### File Transfer Issues
- **Transfer failed**: Check that nodes are connected (`connect` command) and have sufficient storage
- **JSON decode error**: Ensure cloud server is running and nodes are properly registered
- **File not found**: Use `list_files <user>` to verify file exists and get correct file_id

### Connection Issues
- **Cannot connect to server**: Ensure cloud server is started first on port 12345
- **Node registration failed**: Check that node details are entered correctly

### Common Commands
- `stats`: Check overall system health
- `nodes`: View node connection status
- `list_files <user>`: Verify file uploads and locations

## Files

- `cloud.py`: Cloud management class
- `storage_virtual_network.py`: Network simulation
- `storage_virtual_node.py`: Node simulation
- `cloud_server.py`: Cloud server application
- `node_client.py`: Node client application
- `main.py`: Single-process demo
- `Documentation.pdf`: Technical documentation