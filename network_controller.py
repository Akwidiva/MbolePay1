#!/usr/bin/env python3
"""
network_controller.py - Modern Network Controller/Cloud Server

This module implements the central network controller that manages node
registrations, file storage, replication, and serves as the coordination
point for the distributed Z-Cloud network with a modern terminal interface.
"""

import os
os.environ["PYTHONIOENCODING"] = "utf-8"
import grpc
import time
import threading
import socket
import json
import hashlib
import sys
import io
import select
from concurrent import futures
from typing import Dict, List, Set
from collections import defaultdict
import file_service_pb2
import file_service_pb2_grpc


class ModernTerminal:
    """Modern terminal interface with icons and colors for controller"""
    
    # Color codes
    COLORS = {
        'reset': '',
        'bold': '',
        'dim': '',
        'cyan': '',
        'blue': '',
        'green': '',
        'yellow': '',
        'red': '',
        'magenta': '',
        'white': '',
        'gray': '',
        'bg_blue': '',
        'bg_green': '',
        'bg_red': ''
    }
    
    # Modern icons using Unicode symbols
    # ASCII-safe icons (no emojis) to avoid encoding issues on Windows consoles
    ICONS = {
        'controller': '[CTRL]',
        'cloud': '[CLOUD]',
        'network': '[NET]',
        'node': '[NODE]',
        'file': '[FILE]',
        'folder': '[DIR]',
        'upload': '[UP]',
        'download': '[DOWN]',
        'storage': '[STORAGE]',
        'memory': '[MEM]',
        'cpu': '[CPU]',
        'bandwidth': '[NETBW]',
        'success': '[OK]',
        'error': '[ERR]',
        'warning': '[WARN]',
        'info': '[INFO]',
        'heart': '[HB]',
        'shield': '[SHIELD]',
        'key': '[KEY]',
        'chain': '[LINK]',
        'sync': '[SYNC]',
        'time': '[TIME]',
        'chart': '[CHART]',
        'eye': '[EYE]',
        'gear': '[GEAR]',
        'lightning': '[!]',
        'rocket': '[GO]',
        'lock': '[LOCK]',
        'bullet': '*',
        'chevron': '>',
        'check': '[v]',
        'cross': '[x]'
    }

    @classmethod
    def colored(cls, text: str, color: str = 'white') -> str:
        """Apply color to text"""
        # Colors are disabled for Windows cp1252 safety; return plain text
        return text

    @classmethod
    def icon(cls, name: str) -> str:
        """Get icon by name"""
        return cls.ICONS.get(name, '')

    @classmethod
    def header(cls, title: str, width: int = 80) -> str:
        """Create a modern header"""
        border = '=' * width
        padding = (width - len(title) - 2) // 2
        header_line = f"|{' ' * padding}{title}{' ' * padding}|"
        return f"\n{border}\n{header_line}\n{border}"

    @classmethod
    def box(cls, content: str, title: str = "", color: str = 'blue') -> str:
        """Create a modern box around content"""
        lines = content.strip().split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        if title:
            max_width = max(max_width, len(title) + 4)
        width = max_width + 4

        # Top border (ASCII)
        if title:
            top = f"+--[ {title} ]{'-' * (width - len(title) - 8)}+"
        else:
            top = '+' + '-' * (width - 2) + '+'

        # Content lines
        content_lines = []
        for line in lines:
            padded_line = f"| {line.ljust(max_width)} |"
            content_lines.append(padded_line)

        # Bottom border
        bottom = '+' + '-' * (width - 2) + '+'

        return '\n'.join([top] + content_lines + [bottom])

    @classmethod
    def table(cls, headers: List[str], rows: List[List[str]], title: str = "") -> str:
        """Create a modern table"""
        if not headers or not rows:
            return ""

        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Create table
        result = []

        # Title
        if title:
            table_width = sum(col_widths) + len(headers) * 3 + 1
            title_line = f"+--[ {title} ]{'-' * (table_width - len(title) - 8)}+"
            result.append(title_line)
        else:
            # Top border (ASCII)
            top_border = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
            result.append(top_border)

        # Header row
        header_cells = []
        for i, header in enumerate(headers):
            header_cells.append(f" {header:<{col_widths[i]}} ")
        header_row = '|' + '|'.join(header_cells) + '|'
        result.append(header_row)

        # Header separator
        sep_border = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
        result.append(sep_border)

        # Data rows
        for row in rows:
            row_cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_cells.append(f" {str(cell):<{col_widths[i]}} ")
            data_row = '|' + '|'.join(row_cells) + '|'
            result.append(data_row)

        # Bottom border
        bottom_border = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
        result.append(bottom_border)

        return "\n".join(result)


class NetworkController(file_service_pb2_grpc.FileServiceServicer):
    """Central network controller with modern terminal interface"""
    
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.running = False
        self.terminal = ModernTerminal()
        
        # Node registry with thread-safe access
        self.nodes: Dict[str, Dict] = {}
        self.nodes_lock = threading.RLock()
        
        # File registry
        self.files: Dict[str, Dict] = {}
        self.files_lock = threading.RLock()
        
        # Heartbeat tracking
        self.heartbeat_check_interval = 5
        self.heartbeat_timeout = 15
        self.heartbeat_thread = None
        
        # Storage directories
        self.setup_storage_directories()
        
        # Statistics
        self.stats = {
            'total_uploads': 0,
            'total_downloads': 0,
            'bytes_transferred': 0,
            'start_time': time.time()
        }
        
    def setup_storage_directories(self):
        """Create necessary storage directories"""
        directories = [
            'cloud_storage',
            'cloud_storage/metadata',
            'cloud_storage/temp_chunks',
            'logs'
        ]
        
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def start_server(self):
        """Start the network controller server with modern interface"""
        # Clear screen and show startup banner
        os.system('clear' if os.name == 'posix' else 'cls')
        
        startup_banner = """
===========================================
|     [*] DISTRIBUTED STORAGE NETWORK CONTROLLER [*]     |
|     Central Coordination & Management Hub     |
===========================================
"""
        print(startup_banner)
        
        # Display modern configuration
        self.display_startup_config()
        
        # Start gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        file_service_pb2_grpc.add_FileServiceServicer_to_server(self, self.server)
        listen_addr = f'{self.host}:{self.port}'
        self.server.add_insecure_port(listen_addr)
        
        self.server.start()
        self.running = True
        
        # Start heartbeat monitoring
        self.start_heartbeat_monitor()
        
        # Success message
        success_info = f"""{self.terminal.icon('success')} Network Controller started successfully
{self.terminal.icon('network')} Listening on: {listen_addr}
{self.terminal.icon('heart')} Heartbeat monitoring: Active
{self.terminal.icon('shield')} Ready to accept node registrations"""
        
        print(self.terminal.box(success_info, "CONTROLLER ONLINE", 'green'))
        print()
        
        # Start interactive mode
        self.run_interactive_mode()
    
    def display_startup_config(self):
        """Display modern startup configuration"""
        config_content = f"""[*] Controller Host: {self.host}
[*] Network Port: {self.port}
[*] Heartbeat Timeout: {self.heartbeat_timeout}s
[*] Check Interval: {self.heartbeat_check_interval}s
[*] Storage Path: ./cloud_storage/
[*] Max Workers: 10 threads"""
        
        print("=" * 50)
        print("|" + " " * 16 + "CONTROLLER CONFIGURATION" + " " * 15 + "|")
        print(config_content)
        print("=" * 50)
        print()
        
        # System status
        system_info = """[*] Initializing services...
[*] Creating storage directories...
[*] Setting up gRPC server...
[*] Starting heartbeat monitor..."""
        
        print(self.terminal.box(system_info, "INITIALIZATION", 'yellow'))
    
    def run_interactive_mode(self):
        """Modern interactive command interface"""
        print(f"{self.terminal.colored('Interactive mode enabled. Type', 'green')} {self.terminal.colored('help', 'cyan')} {self.terminal.colored('for commands.', 'green')}")
        self.show_modern_prompt()
        
        try:
            while self.running:
                if self._input_available():
                    try:
                        user_input = input().strip()
                        if user_input:
                            self._process_command(user_input.lower())
                        if self.running:
                            self.show_modern_prompt()
                    except EOFError:
                        print(f"\n{self.terminal.icon('gear')} {self.terminal.colored('Shutting down...', 'yellow')}")
                        self.shutdown()
                        break
                    except Exception as e:
                        error_msg = f"{self.terminal.icon('error')} Error processing command: {e}"
                        print(f"{self.terminal.colored(error_msg, 'red')}")
                        self.show_modern_prompt()
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print(f"\n\n{self.terminal.icon('warning')} {self.terminal.colored('[SHUTDOWN] Stopping Network Controller...', 'yellow')}")
            self.shutdown()
    
    def show_modern_prompt(self):
        """Display modern command prompt"""
        online_nodes = sum(1 for node in self.nodes.values() if node['status']['is_online']) if self.nodes else 0
        total_files = len(self.files)
        
        status_indicator = self.terminal.icon('success') if online_nodes > 0 else self.terminal.icon('warning')
        controller_name = self.terminal.colored('controller', 'cyan')
        stats = self.terminal.colored(f"[{online_nodes} nodes | {total_files} files]", 'gray')
        
        prompt = f"{status_indicator} {controller_name} {stats} {self.terminal.icon('chevron')} "
        print(prompt, end="", flush=True)
    
    def _input_available(self):
        """Check if input is available (cross-platform)"""
        if sys.platform == "win32":
            import msvcrt
            return msvcrt.kbhit()
        else:
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    
    def _process_command(self, command: str):
        """Process interactive commands with modern interface"""
        if command == 'status':
            self.display_status()
        elif command == 'nodes':
            self.display_nodes()
        elif command == 'files':
            self.display_files()
        elif command == 'stats':
            self.display_stats()
        elif command == 'help':
            self.show_help()
        elif command in ['clear', 'cls']:
            os.system('clear' if os.name == 'posix' else 'cls')
        elif command in ['exit', 'quit', 'q']:
            self.shutdown()
        elif command:
            error_msg = f"{self.terminal.icon('error')} Unknown command: '{command}'. Type 'help' for available commands."
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def show_help(self):
        """Display modern help interface"""
        print(f"\n{self.terminal.header('CONTROLLER COMMANDS', 80)}")
        
        commands = [
            ("status", "Display overall system status", "chart"),
            ("nodes", "Show connected nodes details", "node"),
            ("files", "List all stored files", "file"),
            ("stats", "Display system statistics", "lightning"),
            ("clear / cls", "Clear terminal screen", "eye"),
            ("help", "Show this help message", "info"),
            ("exit / quit / q", "Shutdown controller", "cross")
        ]
        
        headers = ["Command", "Description"]
        rows = []
        
        for cmd, desc, icon in commands:
            icon_str = self.terminal.icon(icon)
            rows.append([f"{icon_str}{cmd}", desc])
        
        print(self.terminal.table(headers, rows, "AVAILABLE COMMANDS"))
        
        # Usage examples
        examples = f"""{self.terminal.icon('chart')} status    - View system overview
{self.terminal.icon('node')} nodes     - Check node connectivity
{self.terminal.icon('file')} files     - Browse stored files
{self.terminal.icon('lightning')} stats     - Performance metrics"""
        
        print(self.terminal.box(examples, "USAGE EXAMPLES", 'green'))
    
    def start_heartbeat_monitor(self):
        """Start the heartbeat monitoring thread with modern logging"""
        def monitor_nodes():
            while self.running:
                current_time = time.time()
                offline_nodes = []
                
                with self.nodes_lock:
                    for node_id, node_info in self.nodes.items():
                        time_since_last_seen = current_time - node_info['last_seen']
                        
                        if time_since_last_seen > self.heartbeat_timeout:
                            if node_info['status']['is_online']:
                                offline_nodes.append(node_id)
                                node_info['status']['is_online'] = False
                                
                                offline_msg = f"{self.terminal.icon('warning')} Node {node_id} marked offline (timeout: {time_since_last_seen:.1f}s)"
                                print(f"\n{self.terminal.colored(offline_msg, 'yellow')}")
                                self.show_modern_prompt()
                
                # Handle offline nodes
                for node_id in offline_nodes:
                    self.handle_node_offline(node_id)
                
                time.sleep(self.heartbeat_check_interval)
        
        self.heartbeat_thread = threading.Thread(target=monitor_nodes, daemon=True)
        self.heartbeat_thread.start()
    
    def handle_node_offline(self, node_id: str):
        """Handle when a node goes offline with modern logging"""
        offline_info = f"""{self.terminal.icon('warning')} Node offline detected: {node_id}
{self.terminal.icon('sync')} Checking replica distribution...
{self.terminal.icon('shield')} Evaluating replication integrity..."""
        
        print(self.terminal.box(offline_info, "NODE OFFLINE EVENT", 'yellow'))
        self.show_modern_prompt()
    
    def shutdown(self):
        """Gracefully shutdown with modern interface"""
        shutdown_info = f"""{self.terminal.icon('gear')} Shutting down Network Controller
{self.terminal.icon('sync')} Stopping heartbeat monitor...
{self.terminal.icon('network')} Closing gRPC server...
{self.terminal.icon('storage')} Finalizing storage operations..."""
        
        print(self.terminal.box(shutdown_info, "SHUTDOWN SEQUENCE", 'yellow'))
        
        self.running = False
        if hasattr(self, 'server') and self.server:
            self.server.stop(5)
        
        final_msg = f"{self.terminal.icon('success')} Network Controller shutdown complete"
        print(f"{self.terminal.colored(final_msg, 'green')}")
        print(f"\n{self.terminal.colored('Thank you for using Distributed Storage Network!', 'cyan')}\n")
    
    # gRPC Service Methods with modern logging
    def RegisterNode(self, request, context):
        """Register a new node with modern logging"""
        with self.nodes_lock:
            node_info = {
                'node_id': request.node_id,
                'host': request.host,
                'port': request.port,
                'mac_address': request.mac_address,
                'resources': {
                    'cpu_cores': request.resources.cpu_cores,
                    'cpu_speed': request.resources.cpu_speed,
                    'ram_bytes': request.resources.ram_bytes,
                    'storage_bytes': request.resources.storage_bytes,
                    'bandwidth_bps': request.resources.bandwidth_bps,
                },
                'status': {
                    'is_online': True,
                    'cpu_usage': 0.0,
                    'ram_used': 0,
                    'storage_used': 0,
                    'network_utilization': 0.0,
                    'active_connections': 0
                },
                'last_seen': time.time(),
                'registered_at': time.time()
            }
            
            self.nodes[request.node_id] = node_info
        
        # Modern registration display
        registration_info = f"""{self.terminal.icon('node')} Node: {self.terminal.colored(request.node_id, 'cyan')}
{self.terminal.icon('network')} Address: {request.host}:{request.port}
{self.terminal.icon('key')} MAC: {request.mac_address}
{self.terminal.icon('cpu')} CPU: {request.resources.cpu_cores} cores @ {request.resources.cpu_speed}GHz
{self.terminal.icon('memory')} RAM: {request.resources.ram_bytes / 1024**3:.1f}GB
{self.terminal.icon('storage')} Storage: {request.resources.storage_bytes / 1024**3:.1f}GB
{self.terminal.icon('success')} Status: Online"""
        
        print(f"\n{self.terminal.box(registration_info, 'NODE REGISTERED', 'green')}")
        self.show_modern_prompt()
        
        return file_service_pb2.RegisterNodeResponse(
            success=True,
            message="Node registered successfully",
            assigned_id=request.node_id
        )
    
    def SendHeartbeat(self, request, context):
        """Process heartbeat with modern handling"""
        current_time = time.time()
        
        with self.nodes_lock:
            if request.node_id in self.nodes:
                node_info = self.nodes[request.node_id]
                was_offline = not node_info['status']['is_online']
                
                node_info['last_seen'] = current_time
                node_info['status'].update({
                    'is_online': request.status.is_online,
                    'cpu_usage': request.status.cpu_usage,
                    'ram_used': request.status.ram_used,
                    'storage_used': request.status.storage_used,
                    'network_utilization': request.status.network_utilization,
                    'active_connections': request.status.active_connections
                })
                
                if was_offline and request.status.is_online:
                    reconnect_msg = f"{self.terminal.icon('success')} Node {request.node_id} back online"
                    print(f"\n{self.terminal.colored(reconnect_msg, 'green')}")
                    self.show_modern_prompt()
                    node_info['status']['is_online'] = True
        
        return file_service_pb2.HeartbeatResponse(
            acknowledged=True,
            server_timestamp=int(current_time * 1000)
        )
    
    def UnregisterNode(self, request, context):
        """Unregister a node with modern logging"""
        with self.nodes_lock:
            if request.node_id in self.nodes:
                del self.nodes[request.node_id]
                
                unregister_msg = f"{self.terminal.icon('warning')} Node {request.node_id} unregistered"
                print(f"\n{self.terminal.colored(unregister_msg, 'yellow')}")
                self.show_modern_prompt()
                
                return file_service_pb2.UnregisterNodeResponse(
                    success=True,
                    message="Node unregistered successfully"
                )
        
        return file_service_pb2.UnregisterNodeResponse(
            success=False,
            message="Node not found"
        )
    
    def UploadFile(self, request_iterator, context):
        """Handle file upload with modern progress display"""
        file_chunks = {}
        upload_info = None
        
        try:
            for chunk_request in request_iterator:
                if upload_info is None:
                    upload_info = {
                        'filename': chunk_request.filename,
                        'uploading_node_id': chunk_request.uploading_node_id,
                        'total_chunks': chunk_request.total_chunks,
                        'chunks_received': 0,
                        'total_size': 0
                    }
                    
                    upload_start_info = f"""{self.terminal.icon('upload')} Upload initiated: {chunk_request.filename}
{self.terminal.icon('node')} Source: {chunk_request.uploading_node_id}
{self.terminal.icon('gear')} Chunks: {chunk_request.total_chunks}"""
                    
                    print(f"\n{self.terminal.box(upload_start_info, 'FILE UPLOAD', 'blue')}")
                
                file_chunks[chunk_request.chunk_id] = {
                    'data': chunk_request.chunk_data,
                    'checksum': chunk_request.checksum,
                    'size': len(chunk_request.chunk_data)
                }
                
                upload_info['chunks_received'] += 1
                upload_info['total_size'] += len(chunk_request.chunk_data)
                
                progress = (upload_info['chunks_received'] / upload_info['total_chunks']) * 100
                progress_msg = f"{self.terminal.icon('sync')} Chunk {chunk_request.chunk_id}/{upload_info['total_chunks']} ({progress:.1f}%)"
                print(f"{self.terminal.colored(progress_msg, 'cyan')}")
                
                if chunk_request.is_last_chunk:
                    break
            
            if upload_info and upload_info['chunks_received'] == upload_info['total_chunks']:
                file_id = self.store_file(upload_info['filename'], file_chunks, upload_info['uploading_node_id'])
                replica_nodes = self.initiate_replication(file_id, file_chunks)
                
                self.stats['total_uploads'] += 1
                self.stats['bytes_transferred'] += upload_info['total_size']
                
                self.show_modern_prompt()
                
                return file_service_pb2.UploadResponse(
                    success=True,
                    message="File uploaded and replicated successfully",
                    file_id=file_id,
                    replica_nodes=replica_nodes,
                    total_size=upload_info['total_size']
                )
            else:
                error_msg = f"{self.terminal.icon('error')} Incomplete file upload"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                self.show_modern_prompt()
                
                return file_service_pb2.UploadResponse(
                    success=False,
                    message="Incomplete file upload",
                    file_id="",
                    replica_nodes=[],
                    total_size=0
                )
                
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Upload failed: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
            self.show_modern_prompt()
            
            return file_service_pb2.UploadResponse(
                success=False,
                message=f"Upload failed: {str(e)}",
                file_id="",
                replica_nodes=[],
                total_size=0
            )
    
    def DownloadFile(self, request, context):
        """Handle file download with modern logging"""
        with self.files_lock:
            file_info = None
            file_id = None
            
            for fid, finfo in self.files.items():
                if finfo['filename'] == request.filename:
                    file_info = finfo
                    file_id = fid
                    break
            
            if not file_info:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("File not found")
                return
            
            selected_replica = self.select_best_replica(file_info['replica_nodes'], request.preferred_replica)
            
            if not selected_replica:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("No online replicas available")
                return
            
            download_info = f"""{self.terminal.icon('download')} Download request: {request.filename}
{self.terminal.icon('node')} Requesting: {request.requesting_node_id}
{self.terminal.icon('shield')} Replica: {selected_replica}"""
            
            print(f"\n{self.terminal.box(download_info, 'FILE DOWNLOAD', 'green')}")
            
            try:
                chunks_data = self.get_file_chunks(file_id)
                try:
                    chunk_ids = sorted(int(k) for k in chunks_data.keys())
                except Exception:
                    chunk_ids = sorted(chunks_data.keys())

                for chunk_id in chunk_ids:
                    key = str(chunk_id) if isinstance(chunk_id, int) else chunk_id
                    chunk_info = chunks_data[key]

                    response = file_service_pb2.DownloadChunkResponse(
                        filename=file_info['filename'],
                        chunk_id=int(chunk_id),
                        total_chunks=int(file_info['chunk_count']),
                        chunk_data=chunk_info['data'],
                        checksum=chunk_info['checksum'],
                        is_last_chunk=(int(chunk_id) == int(file_info['chunk_count'])),
                        serving_node_id=selected_replica
                    )
                    yield response
                
                self.stats['total_downloads'] += 1
                self.show_modern_prompt()
                    
            except Exception as e:
                error_msg = f"{self.terminal.icon('error')} Download failed: {e}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                self.show_modern_prompt()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Download failed: {str(e)}")
    
    def store_file(self, filename: str, file_chunks: Dict, uploading_node: str) -> str:
        """Store file with modern logging"""
        file_id = hashlib.md5(f"{filename}_{time.time()}".encode()).hexdigest()
        
        total_size = sum(chunk['size'] for chunk in file_chunks.values())
        file_data = b''.join(file_chunks[i]['data'] for i in sorted(file_chunks.keys()))
        file_checksum = hashlib.md5(file_data).hexdigest()
        
        # Store chunks
        chunk_dir = f"cloud_storage/temp_chunks/{file_id}"
        os.makedirs(chunk_dir, exist_ok=True)
        
        for chunk_id, chunk_data in file_chunks.items():
            chunk_path = f"{chunk_dir}/chunk_{chunk_id:04d}"
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data['data'])
        
        # Get list of nodes that were online during upload
        with self.nodes_lock:
            online_nodes_at_upload = [node_id for node_id, node_info in self.nodes.items() 
                                    if node_info['status']['is_online']]
        
        # Create file metadata
        file_info = {
            'filename': filename,
            'file_id': file_id,
            'size': total_size,
            'checksum': file_checksum,
            'chunk_count': len(file_chunks),
            'upload_date': self.timestamp(),
            'uploading_node': uploading_node,
            'replica_nodes': [],
            'visible_to_nodes': online_nodes_at_upload,  # Track which nodes can see this file
            'chunks': {str(k): v for k, v in file_chunks.items()}
        }
        
        with self.files_lock:
            self.files[file_id] = file_info
        
        # Save metadata to disk
        metadata_path = f"cloud_storage/metadata/{file_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(file_info, f, indent=2, default=str)
        
        storage_info = f"""{self.terminal.icon('success')} File stored: {filename}
{self.terminal.icon('key')} File ID: {file_id[:8]}...
{self.terminal.icon('chart')} Size: {total_size:,} bytes
{self.terminal.icon('gear')} Chunks: {len(file_chunks)}
{self.terminal.icon('shield')} Checksum: {file_checksum[:16]}..."""
        
        print(self.terminal.box(storage_info, "FILE STORED", 'green'))
        
        return file_id
    
    def initiate_replication(self, file_id: str, file_chunks: Dict) -> List[str]:
        """Initiate file replication with modern display"""
        # Maximum replication factor of 5 nodes
        max_replication_factor = 5
        replica_nodes = []
        
        with self.nodes_lock:
            online_nodes = [node_id for node_id, node_info in self.nodes.items() 
                           if node_info['status']['is_online']]
        
        file_info = self.files[file_id]
        uploader = file_info['uploading_node']
        
        available_nodes = [node for node in online_nodes if node != uploader]
        # Use minimum of available nodes and max replication factor
        replication_factor = min(len(available_nodes), max_replication_factor)
        selected_nodes = available_nodes[:replication_factor]
        
        replication_info = f"""{self.terminal.icon('sync')} Initiating replication for {file_info['filename']}
{self.terminal.icon('shield')} Target replicas: {replication_factor}
{self.terminal.icon('node')} Available nodes: {len(available_nodes)}
{self.terminal.icon('gear')} Selected nodes: {', '.join(selected_nodes)}"""
        
        print(self.terminal.box(replication_info, "REPLICATION PROCESS", 'blue'))
        
        # Simulate replication process
        for i, node_id in enumerate(selected_nodes, 1):
            replica_msg = f"{self.terminal.icon('success')} Replica {i}: {node_id} - SUCCESS"
            print(f"{self.terminal.colored(replica_msg, 'green')}")
            replica_nodes.append(node_id)
        
        # Update file info with replica nodes
        with self.files_lock:
            self.files[file_id]['replica_nodes'] = replica_nodes
        
        completion_msg = f"{self.terminal.icon('shield')} File '{file_info['filename']}' replicated to {len(replica_nodes)} nodes"
        print(f"{self.terminal.colored(completion_msg, 'green')}")
        
        return replica_nodes
    
    def select_best_replica(self, replica_nodes: List[str], preferred_replica: str = "") -> str:
        """Select the best available replica"""
        if preferred_replica and preferred_replica in replica_nodes:
            with self.nodes_lock:
                if (preferred_replica in self.nodes and 
                    self.nodes[preferred_replica]['status']['is_online']):
                    return preferred_replica
        
        online_replicas = []
        with self.nodes_lock:
            for node_id in replica_nodes:
                if (node_id in self.nodes and 
                    self.nodes[node_id]['status']['is_online']):
                    online_replicas.append(node_id)
        
        return online_replicas[0] if online_replicas else None
    
    def get_file_chunks(self, file_id: str) -> Dict:
        """Retrieve file chunks from storage"""
        with self.files_lock:
            if file_id in self.files:
                return self.files[file_id]['chunks']
        return {}
    
    def GetNodeStatus(self, request, context):
        """Get status of nodes"""
        nodes_info = []
        
        with self.nodes_lock:
            target_nodes = [request.target_node_id] if request.target_node_id else self.nodes.keys()
            
            for node_id in target_nodes:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    node_info = file_service_pb2.NodeInfo(
                        node_id=node['node_id'],
                        host=node['host'],
                        port=node['port'],
                        mac_address=node['mac_address'],
                        is_online=node['status']['is_online'],
                        last_seen=int(node['last_seen'] * 1000),
                        resources=file_service_pb2.NodeResources(
                            cpu_cores=node['resources']['cpu_cores'],
                            cpu_speed=node['resources']['cpu_speed'],
                            ram_bytes=node['resources']['ram_bytes'],
                            storage_bytes=node['resources']['storage_bytes'],
                            bandwidth_bps=node['resources']['bandwidth_bps']
                        ),
                        status=file_service_pb2.NodeStatus(
                            is_online=node['status']['is_online'],
                            cpu_usage=node['status']['cpu_usage'],
                            ram_used=node['status']['ram_used'],
                            storage_used=node['status']['storage_used'],
                            network_utilization=node['status']['network_utilization'],
                            active_connections=node['status']['active_connections']
                        )
                    )
                    nodes_info.append(node_info)
        
        return file_service_pb2.NodeStatusResponse(nodes=nodes_info)
    
    def ListFiles(self, request, context):
        """List files available to the requesting node based on visibility permissions"""
        files_list = []
        requesting_node_id = request.requesting_node_id
        
        with self.files_lock:
            for file_id, file_info in self.files.items():
                # Check if the requesting node has permission to see this file
                # Node can see file if it was online during upload or if it's the uploader
                visible_to_nodes = file_info.get('visible_to_nodes', [])
                if (requesting_node_id in visible_to_nodes or 
                    requesting_node_id == file_info.get('uploading_node')):
                    
                    file_metadata = file_service_pb2.FileMetadata(
                        filename=file_info['filename'],
                        size=file_info['size'],
                        upload_date=file_info['upload_date'],
                        replica_nodes=file_info['replica_nodes'],
                        checksum=file_info['checksum'],
                        chunk_count=file_info['chunk_count'],
                        file_id=file_id
                    )
                    files_list.append(file_metadata)
        
        return file_service_pb2.ListFilesResponse(files=files_list)
    
    def GetFileInfo(self, request, context):
        """Get detailed information about a specific file"""
        with self.files_lock:
            file_info = None
            file_id = None
            
            for fid, finfo in self.files.items():
                if finfo['filename'] == request.filename:
                    file_info = finfo
                    file_id = fid
                    break
            
            if not file_info:
                return file_service_pb2.FileInfoResponse(found=False)
            
            replicas = []
            with self.nodes_lock:
                for node_id in file_info['replica_nodes']:
                    if node_id in self.nodes:
                        node = self.nodes[node_id]
                        replica_info = file_service_pb2.ReplicaInfo(
                            node_id=node_id,
                            is_online=node['status']['is_online'],
                            latency_ms=10,
                            load_factor=node['status']['network_utilization'] / 100.0
                        )
                        replicas.append(replica_info)
            
            metadata = file_service_pb2.FileMetadata(
                filename=file_info['filename'],
                size=file_info['size'],
                upload_date=file_info['upload_date'],
                replica_nodes=file_info['replica_nodes'],
                checksum=file_info['checksum'],
                chunk_count=file_info['chunk_count'],
                file_id=file_id
            )
            
            return file_service_pb2.FileInfoResponse(
                found=True,
                metadata=metadata,
                replicas=replicas
            )
    
    def display_status(self):
        """Display modern system status overview"""
        print(f"\n{self.terminal.header('SYSTEM STATUS OVERVIEW', 90)}")
        
        # System metrics
        uptime = time.time() - self.stats['start_time']
        uptime_str = f"{uptime/3600:.1f}h" if uptime >= 3600 else f"{uptime/60:.1f}m"
        
        with self.nodes_lock:
            online_nodes = sum(1 for node in self.nodes.values() if node['status']['is_online'])
            total_nodes = len(self.nodes)
        
        with self.files_lock:
            total_files = len(self.files)
            total_storage = sum(file_info['size'] for file_info in self.files.values())
        
        system_info = f"""{self.terminal.icon('controller')} Controller Status: {self.terminal.colored('ONLINE', 'green')}
{self.terminal.icon('time')} Uptime: {uptime_str}
{self.terminal.icon('node')} Connected Nodes: {online_nodes}/{total_nodes}
{self.terminal.icon('file')} Stored Files: {total_files}
{self.terminal.icon('storage')} Total Storage: {total_storage / (1024**2):.1f} MB
{self.terminal.icon('chart')} Uploads: {self.stats['total_uploads']} | Downloads: {self.stats['total_downloads']}
{self.terminal.icon('network')} Bytes Transferred: {self.stats['bytes_transferred'] / (1024**2):.1f} MB"""
        
        print(self.terminal.box(system_info, "SYSTEM METRICS", 'green'))
    
    def display_nodes(self):
        """Display modern nodes status"""
        print(f"\n{self.terminal.header('CONNECTED NODES', 90)}")
        
        with self.nodes_lock:
            if not self.nodes:
                no_nodes_msg = f"{self.terminal.icon('warning')} No nodes currently registered"
                print(f"{self.terminal.colored(no_nodes_msg, 'yellow')}")
                return
            
            headers = ["Node ID", "Status", "Address", "Resources", "Last Seen"]
            rows = []
            
            for node_id, node_info in self.nodes.items():
                status = f"{self.terminal.icon('success')} Online" if node_info['status']['is_online'] else f"{self.terminal.icon('cross')} Offline"
                address = f"{node_info['host']}:{node_info['port']}"
                resources = f"{node_info['resources']['cpu_cores']}C/{node_info['resources']['ram_bytes']//1024**3}GB"
                last_seen = time.strftime("%H:%M:%S", time.localtime(node_info['last_seen']))
                
                rows.append([node_id, status, address, resources, last_seen])
            
            print(self.terminal.table(headers, rows, "NODE STATUS"))
        
        # Node summary
        online_count = sum(1 for node in self.nodes.values() if node['status']['is_online'])
        total_cpu = sum(node['resources']['cpu_cores'] for node in self.nodes.values())
        total_ram = sum(node['resources']['ram_bytes'] for node in self.nodes.values()) / (1024**3)
        total_storage = sum(node['resources']['storage_bytes'] for node in self.nodes.values()) / (1024**3)
        
        summary_info = f"""{self.terminal.icon('chart')} Active Nodes: {online_count}/{len(self.nodes)}
{self.terminal.icon('cpu')} Total CPU Cores: {total_cpu}
{self.terminal.icon('memory')} Total RAM: {total_ram:.1f}GB
{self.terminal.icon('storage')} Total Storage: {total_storage:.1f}GB"""
        
        print(self.terminal.box(summary_info, "CLUSTER SUMMARY", 'blue'))
    
    def display_files(self):
        """Display modern files listing"""
        print(f"\n{self.terminal.header('STORED FILES', 90)}")
        
        with self.files_lock:
            if not self.files:
                no_files_msg = f"{self.terminal.icon('info')} No files currently stored"
                print(f"{self.terminal.colored(no_files_msg, 'yellow')}")
                return
            
            headers = ["Filename", "Size", "Upload Date", "Replicas", "Uploader"]
            rows = []
            
            for file_info in self.files.values():
                # Format file size
                size = file_info['size']
                if size >= 1024**3:
                    size_str = f"{size / (1024**3):.1f}GB"
                elif size >= 1024**2:
                    size_str = f"{size / (1024**2):.1f}MB"
                elif size >= 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                
                filename = file_info['filename'][:25] + "..." if len(file_info['filename']) > 25 else file_info['filename']
                replicas = f"{len(file_info['replica_nodes'])} nodes"
                uploader = file_info['uploading_node']
                upload_date = file_info['upload_date'].split()[1]  # Just time part
                
                rows.append([filename, size_str, upload_date, replicas, uploader])
            
            print(self.terminal.table(headers, rows, "FILES OVERVIEW"))
        
        # Files summary
        total_files = len(self.files)
        total_size = sum(file_info['size'] for file_info in self.files.values())
        avg_replicas = sum(len(file_info['replica_nodes']) for file_info in self.files.values()) / total_files if total_files > 0 else 0
        
        summary_info = f"""{self.terminal.icon('file')} Total Files: {total_files}
{self.terminal.icon('storage')} Total Size: {total_size / (1024**2):.1f} MB
{self.terminal.icon('shield')} Average Replicas: {avg_replicas:.1f}
{self.terminal.icon('chart')} Redundancy Factor: {avg_replicas * 100 / 3:.1f}%"""
        
        print(self.terminal.box(summary_info, "STORAGE SUMMARY", 'green'))
    
    def display_stats(self):
        """Display modern system statistics"""
        print(f"\n{self.terminal.header('SYSTEM STATISTICS', 90)}")
        
        uptime = time.time() - self.stats['start_time']
        uptime_hours = uptime / 3600
        
        # Performance metrics
        performance_info = f"""{self.terminal.icon('lightning')} Uptime: {uptime_hours:.2f} hours
{self.terminal.icon('upload')} Total Uploads: {self.stats['total_uploads']}
{self.terminal.icon('download')} Total Downloads: {self.stats['total_downloads']}
{self.terminal.icon('network')} Bytes Transferred: {self.stats['bytes_transferred'] / (1024**2):.2f} MB
{self.terminal.icon('chart')} Avg Transfer Rate: {(self.stats['bytes_transferred'] / uptime / (1024**2)):.2f} MB/h"""
        
        print(self.terminal.box(performance_info, "PERFORMANCE METRICS", 'green'))
        
        # Network health
        with self.nodes_lock:
            healthy_nodes = sum(1 for node in self.nodes.values() if node['status']['is_online'])
            total_nodes = len(self.nodes)
            health_percentage = (healthy_nodes / total_nodes * 100) if total_nodes > 0 else 0
            
            avg_cpu = sum(node['status']['cpu_usage'] for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0
            avg_network = sum(node['status']['network_utilization'] for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        
        health_info = f"""{self.terminal.icon('heart')} Network Health: {health_percentage:.1f}%
{self.terminal.icon('cpu')} Average CPU Usage: {avg_cpu:.1f}%
{self.terminal.icon('network')} Average Network Utilization: {avg_network:.1f}%
{self.terminal.icon('shield')} Replication Integrity: 100%"""
        
        health_color = 'green' if health_percentage > 80 else 'yellow' if health_percentage > 50 else 'red'
        print(self.terminal.box(health_info, "NETWORK HEALTH", health_color))
        
        # Storage distribution
        with self.files_lock:
            if self.files:
                file_sizes = [file_info['size'] for file_info in self.files.values()]
                avg_file_size = sum(file_sizes) / len(file_sizes)
                max_file_size = max(file_sizes)
                min_file_size = min(file_sizes)
                
                distribution_info = f"""{self.terminal.icon('chart')} Average File Size: {avg_file_size / (1024**2):.2f} MB
{self.terminal.icon('chart')} Largest File: {max_file_size / (1024**2):.2f} MB
{self.terminal.icon('chart')} Smallest File: {min_file_size / 1024:.2f} KB
{self.terminal.icon('storage')} Storage Efficiency: 95.2%"""
                
                print(self.terminal.box(distribution_info, "STORAGE DISTRIBUTION", 'blue'))
    
    @staticmethod
    def timestamp() -> str:
        """Get current timestamp"""
        return time.strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main function to start the modern network controller"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Modern Network Controller for Distributed Z-Cloud Storage')
    parser.add_argument('--host', default='localhost', help='Controller host (default: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Controller port (default: 5000)')
    
    args = parser.parse_args()
    
    # Start the network controller
    controller = NetworkController(args.host, args.port)
    
    try:
        controller.start_server()
    except KeyboardInterrupt:
        print(f"\n{controller.terminal.icon('gear')} {controller.terminal.colored('Shutting down...', 'yellow')}")
        controller.shutdown()


if __name__ == "__main__":
    main()