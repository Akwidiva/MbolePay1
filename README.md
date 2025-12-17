# Z-Cloud - Distributed Cloud Storage Network

A console-based simulation of a distributed cloud storage network that demonstrates key concepts in distributed computing, including file transfers, network protocols, threading, remote procedure calls (RPC) via gRPC, dynamic node connections, fault tolerance, and cloud-like storage services.

## Project Structure

```
Z-Cloud/
├── file_service.proto          # gRPC protocol definition
├── file_service_pb2.py         # Generated gRPC messages (auto-generated)
├── file_service_pb2_grpc.py    # Generated gRPC services (auto-generated)
├── node_resources.py           # Node configuration and resource management
├── tcp_ip_processor.py         # TCP/IP stack implementation with detailed logging
├── network_controller.py       # Central network controller/cloud server
├── node.py                     # Storage Z-Cloud node implementation
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── cloud_storage/              # Controller storage directory
├── node_storage/               # Individual node storage directories
└── logs/                       # System logs
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install grpcio grpcio-tools
   ```

3. **Generate gRPC code from protocol buffer definition:**
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto
   ```

## Usage

### Step 1: Start the Network Controller (Cloud Server)

In the first terminal:
```bash
python network_controller.py
```

Expected output:
```
═══════════════════════════════════════════════════════════════
            NETWORK CONTROLLER STARTING
═══════════════════════════════════════════════════════════════
Network Controller Configuration:
├─ Host: localhost
├─ Port: 5000
├─ Heartbeat Timeout: 30s
└─ Storage Location: ./cloud_storage/

[2025-08-18 14:30:15] Network Controller started on localhost:5000
[2025-08-18 14:30:15] Ready to accept node registrations...

controller>
```

Controller commands:
- `status` - Display controller and node status
- `help` - Show available commands
- `exit` - Shutdown controller

### Step 2: Start Z-Cloud Nodes

In separate terminals, start Z-Cloud nodes with different configurations:

**High-Performance Node:**
```bash
python node.py \
  --node-id HighEndVM \
  --port 5001 \
  --cpu 8 \
  --cpu-speed 3.2 \
  --ram 16 \
  --storage 1000 \
  --bandwidth 10000 \
  --mac-address "AA:BB:CC:DD:EE:01"
```

**Medium-Performance Node:**
```bash
python node.py --node-id MediumVM --port 5002 --cpu 4 --ram 8 --storage 500 --bandwidth 1000
```

**Basic Node:**
```bash
python node.py --node-id BasicVM --port 5003 --cpu 2 --ram 4 --storage 250 --bandwidth 500
```

### Step 3: Interact with Nodes

Each node provides an interactive command interface:

```bash
HighEndVM> help

Available commands:
├─ upload <filepath>        - Upload local file to cloud
├─ download <filename>      - Download file from cloud
├─ list_files / ls         - Show all files on cloud
├─ file_info <filename>     - Get detailed file information
├─ status                  - Show node status and resources
└─ exit / quit             - Shutdown node
```

## Detailed Features Demo

### File Upload with TCP/IP Stack Visualization

```bash
HighEndVM> upload /path/to/document.pdf

═══════════════════════════════════════════════════════════════
                    FILE UPLOAD INITIATED
═══════════════════════════════════════════════════════════════
Source File: /path/to/document.pdf
├─ File Size: 2,415,919 bytes (2.3 MB)
├─ Destination: Cloud Storage via Controller
└─ Replication Factor: 3 nodes

[Step 1] FILE CHUNKING
═══════════════════════════════════════════════════════════════
├─ Chunk Size: 65,536 bytes (64 KB)
├─ Total Chunks: 37 chunks
├─ Last Chunk: 18,207 bytes
└─ Chunking Time: 0.023s

Processing chunks through TCP/IP stack...

[CHUNK 1/37] - 65,536 bytes
═══════════════════════════════════════════════════════════════

► APPLICATION LAYER (Layer 7)
┌─────────────────────────────────────────────────────────────┐
│ Raw File Data (Chunk 1)                                    │
│ Size: 65,536 bytes                                         │
│ Data: [25504446...] (PDF Header)                           │
│ Checksum: CRC32 = 0xA1B2C3D4                              │
└─────────────────────────────────────────────────────────────┘

► TRANSPORT LAYER (Layer 4) - TCP SEGMENT
┌─────────────────────────────────────────────────────────────┐
│ TCP Header (20 bytes)                                      │
│ ├─ Source Port: 5001                                       │
│ ├─ Dest Port: 5000 (Controller)                           │
│ ├─ Sequence Number: 1000                                   │
│ ├─ Acknowledgment: 0                                       │
│ ├─ Window Size: 65,535                                     │
│ ├─ Checksum: 0x8F2A                                        │
│ └─ Flags: [PSH, ACK]                                       │
└─────────────────────────────────────────────────────────────┘

► NETWORK LAYER (Layer 3) - IP PACKET
┌─────────────────────────────────────────────────────────────┐
│ IP Header (20 bytes)                                       │
│ ├─ Version: 4                                              │
│ ├─ Total Length: 65,580 bytes                              │
│ ├─ Source IP: 127.0.0.1 (localhost)                       │
│ └─ Dest IP: 127.0.0.1 (localhost)                         │
└─────────────────────────────────────────────────────────────┘

► DATA LINK LAYER (Layer 2) - ETHERNET FRAME
┌─────────────────────────────────────────────────────────────┐
│ Ethernet Header (14 bytes)                                 │
│ ├─ Dest MAC: BB:CC:DD:EE:FF:00 (Controller)               │
│ ├─ Source MAC: AA:BB:CC:DD:EE:01 (HighEndVM)              │
│ └─ EtherType: 0x0800 (IPv4)                               │
└─────────────────────────────────────────────────────────────┘

► PHYSICAL LAYER (Layer 1) - BIT TRANSMISSION
┌─────────────────────────────────────────────────────────────┐
│ Transmission Simulation                                     │
│ ├─ Frame Size: 65,598 bytes = 524,784 bits                │
│ ├─ Bandwidth: 10000 Mbps = 1,310,720,000 bps              │
│ ├─ Transmission Time: 0.000400 seconds                     │
│ └─ Total Time: 0.001400 seconds                            │
└─────────────────────────────────────────────────────────────┘

[TRANSMISSION COMPLETE - Chunk 1]
├─ Bytes Sent: 65,598 bytes (frame)
├─ Payload: 65,536 bytes (actual data)
├─ Overhead: 62 bytes (headers + trailer)
├─ Transmission Time: 0.001400s
└─ Effective Rate: 45.85 MB/s
```

### File Browsing and Download

```bash
HighEndVM> list_files

Available files on cloud:
┌─────────────────┬──────────┬─────────────────────┬───────────────┐
│ Filename        │ Size     │ Upload Date         │ Replicas      │
├─────────────────┼──────────┼─────────────────────┼───────────────┤
│ document.pdf    │ 2.3 MB   │ 2025-08-18 14:30:22 │ CloudNode1, CloudNode2, CloudNode3 │
│ presentation.ppt│ 8.7 MB   │ 2025-08-18 14:28:15 │ CloudNode2, CloudNode4      │
└─────────────────┴──────────┴─────────────────────┴───────────────┘

HighEndVM> file_info document.pdf

File: document.pdf
├─ Size: 2.3 MB (2,415,919 bytes)
├─ Chunks: 37 segments
├─ Upload Date: 2025-08-18 14:30:22
├─ Checksum: a1b2c3d4e5f6...
├─ Available Replicas: 3
│  ├─ CloudNode1 (localhost:5001) - Online ✓
│  ├─ CloudNode2 (localhost:5002) - Online ✓
│  └─ CloudNode3 (localhost:5003) - Offline ✗
└─ Estimated Download Time: 1.2s @ 10000Mbps

HighEndVM> download document.pdf
```

### Node Status Monitoring

```bash
HighEndVM> status

HighEndVM Status:
├─ Network: localhost:5001
├─ MAC: AA:BB:CC:DD:EE:01
├─ CPU: 8 cores @ 3.2 GHz
├─ RAM: 16 GB (Usage: 0.5 GB / 16 GB)
├─ Storage: 1000 GB (Usage: 2.3 GB / 1000 GB)
├─ Bandwidth: 10000 Mbps
├─ Network Usage: 15.2%
├─ Local Files: 3
├─ Replicas Stored: 7
└─ Status: Online ✓
```

### Controller Status Monitoring

```bash
controller> status

═══════════════════════════════════════════════════════════════
               NETWORK CONTROLLER STATUS
═══════════════════════════════════════════════════════════════
Connected Nodes: 3/3
┌─────────────────┬──────────┬────────────────┬────────────┐
│ Node ID         │ Status   │ Host:Port      │ Last Seen  │
├─────────────────┼──────────┼────────────────┼────────────┤
│ HighEndVM       │ Online ✓ │ localhost:5001 │ 14:30:45   │
│ MediumVM        │ Online ✓ │ localhost:5002 │ 14:30:44   │
│ BasicVM         │ Offline ✗│ localhost:5003 │ 14:28:10   │
└─────────────────┴──────────┴────────────────┴────────────┘

Stored Files: 2
Total Storage: 11.0 MB
┌──────────────────────┬──────────┬─────────────────────┬──────────────┐
│ Filename             │ Size     │ Upload Date         │ Replicas     │
├──────────────────────┼──────────┼─────────────────────┼──────────────┤
│ document.pdf         │ 2.3 MB   │ 2025-08-18 14:30:22 │ 3 nodes      │
│ presentation.ppt     │ 8.7 MB   │ 2025-08-18 14:28:15 │ 2 nodes      │
└──────────────────────┴──────────┴─────────────────────┴──────────────┘
═══════════════════════════════════════════════════════════════
```

## Key Features Demonstrated

### 1. **TCP/IP Protocol Stack Simulation**
- Complete encapsulation/decapsulation through all 7 layers
- Detailed header information for each protocol layer
- Bandwidth-based transmission time calculations
- CRC32 checksums for data integrity verification

### 2. **Distributed File Storage**
- Automatic file chunking (64KB chunks)
- Multi-node replication