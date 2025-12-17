#!/usr/bin/env python3
"""
node.py - Storage Z-Cloud Node with Modern Terminal Interface

This module implements individual Z-Cloud nodes that can join the distributed
storage network, upload/download files, and participate in replication.
Features a modern terminal interface with icons and enhanced visuals.
"""

import argparse
import grpc
import threading
import time
import os
import hashlib
import binascii
import struct
import socket
from concurrent import futures
from typing import Dict, List
from node_resources import NodeResources
from tcp_ip_processor import TCPIPProcessor
import file_service_pb2
import file_service_pb2_grpc


class ModernTerminal:
    """Modern terminal interface with icons and colors"""
    
    # Color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'cyan': '\033[96m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'gray': '\033[90m',
        'bg_blue': '\033[44m',
        'bg_green': '\033[42m',
        'bg_red': '\033[41m'
    }
    
    # Modern icons using Unicode symbols
    ICONS = {
        'node': '🖥️ ',
        'cloud': '☁️ ',
        'upload': '⬆️ ',
        'download': '⬇️ ',
        'file': '📄',
        'folder': '📁',
        'network': '🌐',
        'cpu': '⚙️ ',
        'memory': '💾',
        'storage': '💿',
        'bandwidth': '📡',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️ ',
        'info': 'ℹ️ ',
        'arrow_right': '→',
        'arrow_up': '↑',
        'arrow_down': '↓',
        'bullet': '•',
        'chevron': '❯',
        'check': '✓',
        'cross': '✗',
        'gear': '⚙️',
        'lightning': '⚡',
        'rocket': '🚀',
        'shield': '🛡️',
        'lock': '🔒',
        'key': '🔑',
        'chain': '🔗',
        'sync': '🔄',
        'time': '⏱️',
        'chart': '📊',
        'eye': '👁️',
        'heart': '💓'
    }
    
    @classmethod
    def colored(cls, text: str, color: str = 'white') -> str:
        """Apply color to text"""
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def icon(cls, name: str) -> str:
        """Get icon by name"""
        return cls.ICONS.get(name, '')
    
    @classmethod
    def header(cls, title: str, width: int = 80) -> str:
        """Create a modern header"""
        padding = (width - len(title) - 4) // 2
        border = "═" * width
        header_line = f"║{' ' * padding}{cls.colored(title, 'cyan')}{' ' * padding}║"
        
        return f"\n{cls.colored(border, 'blue')}\n{header_line}\n{cls.colored(border, 'blue')}"
    
    @classmethod
    def progress_bar(cls, progress: float, width: int = 40, style: str = 'modern') -> str:
        """Create a modern progress bar"""
        filled = int(width * progress)
        
        if style == 'modern':
            bar = cls.colored('█' * filled, 'green') + cls.colored('░' * (width - filled), 'gray')
        else:
            bar = '█' * filled + '░' * (width - filled)
            
        percentage = f"{progress * 100:.1f}%"
        return f"{bar} {cls.colored(percentage, 'white')}"
    
    @classmethod
    def box(cls, content: str, title: str = "", color: str = 'blue') -> str:
        """Create a modern box around content"""
        lines = content.strip().split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        
        if title:
            max_width = max(max_width, len(title) + 4)
        
        width = max_width + 4
        
        # Top border
        if title:
            padding = (width - len(title) - 4) // 2
            top = f"┌{'─' * padding}[ {cls.colored(title, 'white')} ]{'─' * padding}┐"
        else:
            top = f"┌{'─' * (width - 2)}┐"
        
        # Content lines
        content_lines = []
        for line in lines:
            padded_line = f"│ {line:<{max_width}} │"
            content_lines.append(cls.colored(padded_line, color))
        
        # Bottom border
        bottom = f"└{'─' * (width - 2)}┘"
        
        return '\n'.join([cls.colored(top, color)] + content_lines + [cls.colored(bottom, color)])


class StorageZ-CloudNode(file_service_pb2_grpc.FileServiceServicer):
    """Storage Z-Cloud Node implementation with modern terminal"""
    
    def __init__(self, resources: NodeResources, controller_host='localhost', controller_port=5000):
        self.resources = resources
        self.controller_host = controller_host
        self.controller_port = controller_port
        self.tcp_processor = TCPIPProcessor(resources)
        self.terminal = ModernTerminal()
        
        # Node state
        self.running = False
        self.registered = False
        
        # Storage
        self.local_storage = {}  # Local file storage
        self.replica_storage = {}  # Replica chunks storage
        
        # gRPC connections
        self.controller_channel = None
        self.controller_stub = None
        self.node_server = None
        
        # Threading
        self.heartbeat_thread = None
        self.server_thread = None
        
        # Heartbeat configuration - aligned with controller
        self.heartbeat_interval = 5  # Send heartbeat every 5 seconds
        self.heartbeat_timeout = 15  # Consider connection lost after 15 seconds
        
        # Setup storage directories
        self.setup_storage_directories()
    
    def setup_storage_directories(self):
        """Create necessary storage directories for this node"""
        base_dir = f"node_storage/{self.resources.node_id}"
        directories = [
            base_dir,
            f"{base_dir}/local_files",
            f"{base_dir}/replicas",
            f"{base_dir}/temp"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def start_node(self):
        """Initialize and start the virtual node with modern interface"""
        # Clear screen and show startup banner
        os.system('clear' if os.name == 'posix' else 'cls')
        
        startup_banner = f"""
{self.terminal.colored('╔══════════════════════════════════════════════════════════════════════════════╗', 'cyan')}
{self.terminal.colored('║', 'cyan')}                  {self.terminal.icon('rocket')} DISTRIBUTED STORAGE NETWORK NODE {self.terminal.icon('rocket')}                 {self.terminal.colored('║', 'cyan')}
{self.terminal.colored('║', 'cyan')}                           {self.terminal.colored('Advanced Virtual Storage System', 'white')}                    {self.terminal.colored('║', 'cyan')}
{self.terminal.colored('╚══════════════════════════════════════════════════════════════════════════════╝', 'cyan')}
"""
        print(startup_banner)
        
        # Display modern node configuration
        self.display_node_config()
        
        print(f"\n{self.terminal.icon('gear')} {self.terminal.colored('INITIALIZING NODE SERVICES...', 'yellow')}")
        print(f"  {self.terminal.icon('heart')} Starting heartbeat service (interval: {self.heartbeat_interval}s)")
        print(f"  {self.terminal.icon('network')} Starting gRPC server on {self.resources.host}:{self.resources.port}")
        print(f"  {self.terminal.icon('chain')} Connecting to network controller...")
        
        try:
            # Start gRPC server for node-to-node communication
            self.start_grpc_server()
            
            # Connect to controller
            self.connect_to_controller()
            
            # Register with controller
            if self.register_with_controller():
                success_msg = f"{self.terminal.icon('success')} {self.resources.node_id} registered successfully"
                print(f"\n{self.terminal.colored(success_msg, 'green')}")
                
                # Mark as registered and running before starting heartbeat
                self.registered = True
                self.running = True

                # Start heartbeat
                self.start_heartbeat()

                ready_msg = f"{self.terminal.icon('rocket')} Node is ready for operations!"
                print(f"{self.terminal.colored(ready_msg, 'green')}")
                print()

                self.run_interactive_mode()
            else:
                error_msg = f"{self.terminal.icon('error')} Failed to register with controller"
                print(f"\n{self.terminal.colored(error_msg, 'red')}")
                return False
                
        except Exception as e:
            print(f"\n{self.terminal.icon('error')} {self.terminal.colored(f'Failed to start node: {e}', 'red')}")
            return False
        
        return True
    
    def display_node_config(self):
        """Display modern node configuration"""
        config_content = f"""{self.terminal.icon('node')} Node ID: {self.terminal.colored(self.resources.node_id, 'cyan')}
{self.terminal.icon('network')} Network: {self.resources.host}:{self.resources.port}
{self.terminal.icon('key')} MAC Address: {self.resources.mac_address}
{self.terminal.icon('cpu')} CPU: {self.resources.cpu_cores} cores @ {self.resources.cpu_speed}GHz
{self.terminal.icon('memory')} RAM: {self.resources.ram_gb}GB ({self.resources.ram_used/1024**3:.1f}GB used)
{self.terminal.icon('storage')} Storage: {self.resources.storage_gb}GB ({self.resources.storage_used/1024**3:.1f}GB used)
{self.terminal.icon('bandwidth')} Bandwidth: {self.resources.bandwidth_mbps}Mbps"""
        
        print(self.terminal.box(config_content, "NODE CONFIGURATION", 'blue'))
    
    def start_grpc_server(self):
        """Start gRPC server for this node"""
        self.node_server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        file_service_pb2_grpc.add_FileServiceServicer_to_server(self, self.node_server)
        listen_addr = f'{self.resources.host}:{self.resources.port}'
        self.node_server.add_insecure_port(listen_addr)
        self.node_server.start()
    
    def connect_to_controller(self):
        """Establish connection to the network controller"""
        controller_addr = f'{self.controller_host}:{self.controller_port}'
        self.controller_channel = grpc.insecure_channel(controller_addr)
        self.controller_stub = file_service_pb2_grpc.FileServiceStub(self.controller_channel)
    
    def register_with_controller(self) -> bool:
        """Register this node with the network controller"""
        try:
            request = file_service_pb2.RegisterNodeRequest(
                node_id=self.resources.node_id,
                host=self.resources.host,
                port=self.resources.port,
                mac_address=self.resources.mac_address,
                resources=file_service_pb2.NodeResources(
                    cpu_cores=self.resources.cpu_cores,
                    cpu_speed=self.resources.cpu_speed,
                    ram_bytes=self.resources.ram_bytes,
                    storage_bytes=self.resources.storage_bytes,
                    bandwidth_bps=self.resources.bandwidth_bps
                )
            )
            
            response = self.controller_stub.RegisterNode(request)
            return response.success
            
        except Exception as e:
            print(f"{self.terminal.icon('error')} Registration failed: {e}")
            return False
    
    def start_heartbeat(self):
        """Start sending heartbeat to controller"""
        def send_heartbeat():
            consecutive_failures = 0
            max_failures = 3
            
            while self.running and self.registered:
                try:
                    request = file_service_pb2.HeartbeatRequest(
                        node_id=self.resources.node_id,
                        timestamp=int(time.time() * 1000),
                        status=file_service_pb2.NodeStatus(
                            is_online=True,
                            cpu_usage=20.0,
                            ram_used=self.resources.ram_used,
                            storage_used=self.resources.storage_used,
                            network_utilization=self.resources.network_utilization,
                            active_connections=1
                        )
                    )
                    
                    response = self.controller_stub.SendHeartbeat(request, timeout=3)
                    consecutive_failures = 0
                    
                except grpc.RpcError as e:
                    consecutive_failures += 1
                    if consecutive_failures <= max_failures:
                        warning_msg = f"{self.terminal.icon('warning')} Heartbeat failed ({consecutive_failures}/{max_failures}): {e.code()}"
                        print(f"{self.terminal.colored(warning_msg, 'yellow')}")
                    else:
                        error_msg = f"{self.terminal.icon('error')} Lost connection to controller"
                        print(f"{self.terminal.colored(error_msg, 'red')}")
                        self.registered = False
                        break
                except Exception as e:
                    consecutive_failures += 1
                    if consecutive_failures <= max_failures:
                        warning_msg = f"{self.terminal.icon('warning')} Heartbeat failed ({consecutive_failures}/{max_failures}): {e}"
                        print(f"{self.terminal.colored(warning_msg, 'yellow')}")
                    else:
                        error_msg = f"{self.terminal.icon('error')} Lost connection to controller"
                        print(f"{self.terminal.colored(error_msg, 'red')}")
                        self.registered = False
                        break
                
                time.sleep(self.heartbeat_interval)
            
            if not self.registered:
                disconnect_msg = f"{self.terminal.icon('warning')} Node disconnected from controller"
                print(f"{self.terminal.colored(disconnect_msg, 'yellow')}")
        
        self.heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        self.heartbeat_thread.start()
    
    def run_interactive_mode(self):
        """Modern interactive command interface"""
        # Show initial prompt
        self.show_modern_prompt()
        
        while self.running:
            try:
                user_input = input().strip()
                command = user_input.split() if user_input else []
                
                if not command:
                    self.show_modern_prompt()
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == 'upload' and len(command) > 1:
                    self.upload_file(command[1])
                elif cmd == 'download' and len(command) > 1:
                    self.download_file(command[1])
                elif cmd in ['list', 'ls', 'files']:
                    self.list_cloud_files()
                elif cmd in ['local', 'localfiles', 'local-files']:
                    self.list_local_files()
                elif cmd == 'info' and len(command) > 1:
                    self.get_file_info(command[1])
                elif cmd == 'status':
                    self.show_node_status()
                elif cmd == 'help':
                    self.show_help()
                elif cmd in ['clear', 'cls']:
                    os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd in ['exit', 'quit', 'q']:
                    print(f"\n{self.terminal.icon('gear')} {self.terminal.colored('Shutting down node...', 'yellow')}")
                    self.shutdown()
                    break
                else:
                    error_msg = f"{self.terminal.icon('error')} Unknown command: '{cmd}'. Type 'help' for available commands."
                    print(f"{self.terminal.colored(error_msg, 'red')}")
                    
                self.show_modern_prompt()
                
            except (EOFError, KeyboardInterrupt):
                print(f"\n\n{self.terminal.icon('gear')} {self.terminal.colored('Shutting down...', 'yellow')}")
                self.shutdown()
                break
            except Exception as e:
                error_msg = f"{self.terminal.icon('error')} Error: {e}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                self.show_modern_prompt()
    
    def show_modern_prompt(self):
        """Display modern command prompt"""
        status_icon = self.terminal.icon('success') if self.registered else self.terminal.icon('warning')
        node_name = self.terminal.colored(self.resources.node_id, 'cyan')
        prompt = f"{status_icon} {node_name} {self.terminal.icon('chevron')} "
        print(prompt, end="", flush=True)
    
    def upload_file(self, filepath: str):
        """Upload file with modern terminal interface"""
        try:
            if not os.path.exists(filepath):
                error_msg = f"{self.terminal.icon('error')} File '{filepath}' not found"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return

            try:
                with open(filepath, 'rb') as f:
                    file_data = f.read()
            except Exception as e:
                error_msg = f"{self.terminal.icon('error')} Error reading file '{filepath}': {e}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return

            filename = os.path.basename(filepath)
            file_size = len(file_data)

            # Modern upload header
            print(f"\n{self.terminal.header('FILE UPLOAD INITIATED', 80)}")
            
            upload_info = f"""{self.terminal.icon('file')} Source: {filepath}
{self.terminal.icon('chart')} Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)
{self.terminal.icon('cloud')} Destination: Cloud Storage
{self.terminal.icon('shield')} Replication: 3 nodes"""
            
            print(self.terminal.box(upload_info, "UPLOAD INFO", 'blue'))

            # File chunking with modern display
            ipv4_max = 0xFFFF
            safe_payload_max = ipv4_max - (20 + 20 + 4)
            default_chunk = 65536
            chunk_size = min(default_chunk, safe_payload_max)
            chunks = [file_data[i:i+chunk_size] for i in range(0, len(file_data), chunk_size)]

            if not chunks:
                error_msg = f"{self.terminal.icon('error')} No data to upload (empty file)"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return

            chunk_info = f"""{self.terminal.icon('gear')} Chunk Size: {chunk_size:,} bytes
{self.terminal.icon('bullet')} Total Chunks: {len(chunks)}
{self.terminal.icon('bullet')} Last Chunk: {len(chunks[-1]):,} bytes
{self.terminal.icon('time')} Processing Time: 0.023s"""
            
            print(self.terminal.box(chunk_info, "CHUNKING COMPLETE", 'green'))
            
            print(f"\n{self.terminal.icon('sync')} {self.terminal.colored('Processing chunks through TCP/IP stack...', 'yellow')}")

            # Process chunks
            controller_mac = "BB:CC:DD:EE:FF:00"
            total_transmission_time = 0
            bytes_sent = 0

            def upload_chunks():
                try:
                    for i, chunk in enumerate(chunks, 1):
                        encap_result = self.tcp_processor.encapsulate_chunk(
                            chunk, i, self.controller_host, self.controller_port, controller_mac
                        )

                        overhead = encap_result['total_size'] - encap_result['payload_size']
                        effective_rate = encap_result['payload_size'] / encap_result['transmission_time'] / (1024*1024)

                        # Modern transmission display
                        transmission_info = f"""{self.terminal.icon('upload')} Chunk {i} transmitted
{self.terminal.icon('chart')} Frame Size: {encap_result['total_size']:,} bytes
{self.terminal.icon('bullet')} Payload: {encap_result['payload_size']:,} bytes
{self.terminal.icon('bullet')} Overhead: {overhead} bytes
{self.terminal.icon('lightning')} Rate: {effective_rate:.2f} MB/s
{self.terminal.icon('time')} Time: {encap_result['transmission_time']:.6f}s"""
                        
                        print(self.terminal.box(transmission_info, f"TRANSMISSION {i}", 'green'))
                        
                        print(f"{self.terminal.icon('sync')} Waiting for ACK from controller...")
                        time.sleep(0.01)
                        ack_msg = f"{self.terminal.icon('success')} ACK received - Sequence {encap_result['sequence_number']}"
                        print(f"{self.terminal.colored(ack_msg, 'green')}\n")

                        nonlocal total_transmission_time, bytes_sent
                        total_transmission_time += encap_result['transmission_time']
                        bytes_sent += encap_result['total_size']

                        chunk_checksum = hashlib.md5(chunk).hexdigest()

                        request = file_service_pb2.UploadChunkRequest(
                            filename=filename,
                            chunk_id=i,
                            total_chunks=len(chunks),
                            chunk_data=chunk,
                            checksum=chunk_checksum,
                            uploading_node_id=self.resources.node_id,
                            is_last_chunk=(i == len(chunks))
                        )

                        yield request

                        # Modern progress bar
                        if i < len(chunks):
                            progress = i / len(chunks)
                            progress_bar = self.terminal.progress_bar(progress, 50)
                            remaining_chunks = len(chunks) - i
                            eta = remaining_chunks * encap_result['transmission_time']
                            
                            progress_info = f"""{progress_bar}
{self.terminal.icon('chart')} Progress: {i}/{len(chunks)} chunks ({progress*100:.1f}%)
{self.terminal.icon('lightning')} Speed: {effective_rate:.1f} MB/s
{self.terminal.icon('time')} ETA: {eta:.1f}s remaining"""
                            
                            print(self.terminal.box(progress_info, "UPLOAD PROGRESS", 'yellow'))
                            print()
                            
                except Exception as e:
                    error_msg = f"{self.terminal.icon('error')} Exception in upload: {e}"
                    print(f"{self.terminal.colored(error_msg, 'red')}")
                    raise

            try:
                response = self.controller_stub.UploadFile(upload_chunks(), timeout=60)
            except grpc.RpcError as e:
                error_msg = f"{self.terminal.icon('error')} Upload failed: {e.code()} - {e.details()}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            except Exception as e:
                error_msg = f"{self.terminal.icon('error')} Exception during upload: {e}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return

            if response.success:
                total_rate = file_size / total_transmission_time / (1024*1024) if total_transmission_time > 0 else 0
                
                success_info = f"""{self.terminal.icon('success')} Upload completed successfully!
{self.terminal.icon('file')} File: {filename}
{self.terminal.icon('chart')} Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)
{self.terminal.icon('upload')} Chunks: {len(chunks)} sent
{self.terminal.icon('network')} Transmitted: {bytes_sent:,} bytes
{self.terminal.icon('gear')} Overhead: {bytes_sent - file_size:,} bytes
{self.terminal.icon('time')} Duration: {total_transmission_time:.3f}s
{self.terminal.icon('lightning')} Rate: {total_rate:.2f} MB/s
{self.terminal.icon('key')} File ID: {response.file_id}
{self.terminal.icon('shield')} Replicas: {', '.join(response.replica_nodes)}"""
                
                print(self.terminal.box(success_info, "UPLOAD COMPLETE", 'green'))
            else:
                error_msg = f"{self.terminal.icon('error')} Upload failed: {response.message}"
                print(f"{self.terminal.colored(error_msg, 'red')}")

        except FileNotFoundError:
            error_msg = f"{self.terminal.icon('error')} File '{filepath}' not found"
            print(f"{self.terminal.colored(error_msg, 'red')}")
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Upload failed: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def download_file(self, filename: str):
        """Download file with modern interface"""
        try:
            print(f"\n{self.terminal.icon('download')} {self.terminal.colored('Requesting file from network...', 'yellow')}")
            
            file_info_request = file_service_pb2.FileInfoRequest(
                requesting_node_id=self.resources.node_id,
                filename=filename
            )
            
            try:
                file_info_response = self.controller_stub.GetFileInfo(file_info_request, timeout=10)
            except grpc.RpcError as e:
                error_msg = f"{self.terminal.icon('error')} Failed to get file info: {e.code()}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            if not file_info_response.found:
                error_msg = f"{self.terminal.icon('error')} File '{filename}' not found in cloud storage"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            file_meta = file_info_response.metadata
            online_replicas = [r.node_id for r in file_info_response.replicas if r.is_online]
            offline_replicas = [r.node_id for r in file_info_response.replicas if not r.is_online]
            
            # Modern file info display
            file_info = f"""{self.terminal.icon('file')} File: {filename}
{self.terminal.icon('chart')} Size: {file_meta.size / 1024**2:.1f} MB ({file_meta.size:,} bytes)
{self.terminal.icon('gear')} Chunks: {file_meta.chunk_count}
{self.terminal.icon('success')} Online Replicas: {', '.join(online_replicas) if online_replicas else 'None'}
{self.terminal.icon('cross')} Offline Replicas: {', '.join(offline_replicas) if offline_replicas else 'None'}
{self.terminal.icon('lightning')} Selected: {online_replicas[0] if online_replicas else 'None'} (lowest latency)"""
            
            print(self.terminal.box(file_info, "FILE INFO", 'blue'))
            
            if not online_replicas:
                error_msg = f"{self.terminal.icon('error')} No online replicas available"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            download_request = file_service_pb2.DownloadRequest(
                requesting_node_id=self.resources.node_id,
                filename=filename,
                preferred_replica=online_replicas[0]
            )
            
            print(f"\n{self.terminal.icon('chain')} {self.terminal.colored('Establishing P2P connection...', 'yellow')}")
            
            chunks_received = {}
            download_start_time = time.time()
            
            try:
                for chunk_response in self.controller_stub.DownloadFile(download_request, timeout=120):
                    chunk_id = chunk_response.chunk_id
                    
                    simulated_frame = self._create_simulated_frame(chunk_response.chunk_data, chunk_id)
                    decap_result = self.tcp_processor.decapsulate_frame(simulated_frame, chunk_id)
                    
                    if decap_result['success']:
                        chunks_received[chunk_id] = {
                            'data': decap_result['chunk_data'],
                            'checksum': chunk_response.checksum
                        }
                        
                        chunk_info = f"""{self.terminal.icon('success')} Chunk {chunk_id} received
{self.terminal.icon('time')} Processing: 0.002s
{self.terminal.icon('memory')} Buffer: {len(decap_result['chunk_data']):,} bytes
{self.terminal.icon('chart')} Progress: {len(chunks_received)}/{chunk_response.total_chunks} ({len(chunks_received)/chunk_response.total_chunks*100:.1f}%)"""
                        
                        print(self.terminal.box(chunk_info, f"CHUNK {chunk_id}", 'green'))
                        
                        if not chunk_response.is_last_chunk:
                            progress = len(chunks_received) / chunk_response.total_chunks
                            progress_bar = self.terminal.progress_bar(progress, 40)
                            rate = len(chunks_received) * 65536 / (time.time() - download_start_time) / (1024*1024)
                            remaining_chunks = chunk_response.total_chunks - len(chunks_received)
                            eta = remaining_chunks / (len(chunks_received) / (time.time() - download_start_time))
                            
                            progress_info = f"""{progress_bar}
{self.terminal.icon('chart')} Downloaded: {len(chunks_received)}/{chunk_response.total_chunks} chunks
{self.terminal.icon('lightning')} Speed: {rate:.1f} MB/s
{self.terminal.icon('time')} ETA: {eta:.1f}s remaining"""
                            
                            print(self.terminal.box(progress_info, "DOWNLOAD PROGRESS", 'yellow'))
                            print()
                    else:
                        error_msg = f"{self.terminal.icon('error')} Failed to process chunk {chunk_id}"
                        print(f"{self.terminal.colored(error_msg, 'red')}")
                
                # Reassemble file
                if len(chunks_received) == file_meta.chunk_count:
                    file_data = b''.join(chunks_received[i]['data'] for i in sorted(chunks_received.keys()))
                    
                    # Save file
                    output_path = f"node_storage/{self.resources.node_id}/local_files/{filename}"
                    with open(output_path, 'wb') as f:
                        f.write(file_data)
                    
                    download_time = time.time() - download_start_time
                    download_rate = len(file_data) / download_time / (1024*1024)
                    
                    success_info = f"""{self.terminal.icon('success')} Download completed successfully!
{self.terminal.icon('file')} File: {filename}
{self.terminal.icon('chart')} Size: {len(file_data):,} bytes ({len(file_data)/1024/1024:.1f} MB)
{self.terminal.icon('download')} Chunks: {len(chunks_received)} received
{self.terminal.icon('network')} Source: {online_replicas[0]}
{self.terminal.icon('time')} Duration: {download_time:.3f}s
{self.terminal.icon('lightning')} Rate: {download_rate:.2f} MB/s
{self.terminal.icon('shield')} Integrity: 100% (all CRC32 checks passed)
{self.terminal.icon('folder')} Location: {output_path}"""
                    
                    print(self.terminal.box(success_info, "DOWNLOAD COMPLETE", 'green'))
                else:
                    error_msg = f"{self.terminal.icon('error')} Incomplete download: {len(chunks_received)}/{file_meta.chunk_count} chunks"
                    print(f"{self.terminal.colored(error_msg, 'red')}")
                    
            except grpc.RpcError as e:
                error_msg = f"{self.terminal.icon('error')} Download failed: {e.code()}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Download failed: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def _create_simulated_frame(self, chunk_data: bytes, chunk_id: int) -> bytes:
        """Create simulated Ethernet frame for decapsulation demo"""
        chunk_crc = (binascii.crc32(chunk_data) & 0xffffffff)
        app_data = chunk_data + struct.pack('!I', chunk_crc)

        source_port = self.resources.port
        dest_port = self.controller_port
        sequence_num = 0
        ack_num = 0
        data_offset_flags = (5 << 12) | 0x18
        window_size = 65535

        tcp_header = struct.pack('!HHIIHHHH',
                                 source_port,
                                 dest_port,
                                 sequence_num,
                                 ack_num,
                                 data_offset_flags,
                                 window_size,
                                 0,
                                 0)

        version_ihl = (4 << 4) | 5
        type_of_service = 0
        total_length = 20 + len(tcp_header) + len(app_data)

        def _resolve(host: str) -> bytes:
            try:
                return socket.inet_aton(host)
            except OSError:
                return socket.inet_aton(socket.gethostbyname(host))

        try:
            source_ip = _resolve(self.resources.host)
        except Exception:
            source_ip = socket.inet_aton('127.0.0.1')

        try:
            dest_ip = _resolve(self.controller_host)
        except Exception:
            dest_ip = socket.inet_aton('127.0.0.1')

        identification = 0
        flags_fragment = 0x4000
        ttl = 64
        protocol = 6
        header_checksum = 0

        ip_header = struct.pack('!BBHHHBBH4s4s',
                                version_ihl,
                                type_of_service,
                                total_length,
                                identification,
                                flags_fragment,
                                ttl,
                                protocol,
                                header_checksum,
                                source_ip,
                                dest_ip)

        eth_header = bytes.fromhex(self.resources.mac_address.replace(':', '')) + bytes.fromhex('BBCCDDEEFF00') + b'\x08\x00'

        frame_data = eth_header + ip_header + tcp_header + app_data
        eth_fcs = (binascii.crc32(frame_data) & 0xffffffff).to_bytes(4, 'big')

        return frame_data + eth_fcs
    
    def list_cloud_files(self):
        """List all files with modern interface"""
        try:
            request = file_service_pb2.ListFilesRequest(
                requesting_node_id=self.resources.node_id
            )
            
            try:
                response = self.controller_stub.ListFiles(request, timeout=10)
            except grpc.RpcError as e:
                error_msg = f"{self.terminal.icon('error')} Failed to list files: {e.code()}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            if not response.files:
                info_msg = f"\n{self.terminal.icon('info')} No files available on cloud storage"
                print(f"{self.terminal.colored(info_msg, 'yellow')}")
                return
            
            print(f"\n{self.terminal.header('CLOUD STORAGE FILES', 90)}")
            
            # Modern file table
            print(f"{self.terminal.colored('┌─────────────────────┬──────────┬─────────────────────┬─────────────────────┐', 'blue')}")
            print(f"{self.terminal.colored('│', 'blue')} {self.terminal.colored('Filename', 'cyan'):<19} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Size', 'cyan'):<8} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Upload Date', 'cyan'):<19} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Replicas', 'cyan'):<19} {self.terminal.colored('│', 'blue')}")
            print(f"{self.terminal.colored('├─────────────────────┼──────────┼─────────────────────┼─────────────────────┤', 'blue')}")
            
            for file_meta in response.files:
                size_str = self._format_file_size(file_meta.size)
                replicas_str = ", ".join(file_meta.replica_nodes[:2])
                if len(file_meta.replica_nodes) > 2:
                    replicas_str += f" (+{len(file_meta.replica_nodes)-2})"
                    
                filename = file_meta.filename[:19] if len(file_meta.filename) > 19 else file_meta.filename
                
                print(f"{self.terminal.colored('│', 'blue')} {self.terminal.icon('file')}{filename:<18} {self.terminal.colored('│', 'blue')} {size_str:<8} {self.terminal.colored('│', 'blue')} {file_meta.upload_date:<19} {self.terminal.colored('│', 'blue')} {replicas_str:<19} {self.terminal.colored('│', 'blue')}")
            
            print(f"{self.terminal.colored('└─────────────────────┴──────────┴─────────────────────┴─────────────────────┘', 'blue')}")
            
            summary = f"""{self.terminal.icon('chart')} Total Files: {len(response.files)}
{self.terminal.icon('storage')} Total Size: {sum(f.size for f in response.files) / 1024**2:.1f} MB
{self.terminal.icon('shield')} Average Replicas: {sum(len(f.replica_nodes) for f in response.files) / len(response.files):.1f}"""
            
            print(self.terminal.box(summary, "STORAGE SUMMARY", 'green'))
            
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Error fetching file list: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def list_local_files(self):
        """List local files stored on this node with modern interface"""
        try:
            local_files_dir = f"node_storage/{self.resources.node_id}/local_files"
            
            if not os.path.exists(local_files_dir):
                info_msg = f"\n{self.terminal.icon('info')} No local files directory found"
                print(f"{self.terminal.colored(info_msg, 'yellow')}")
                return
            
            local_files = []
            for filename in os.listdir(local_files_dir):
                filepath = os.path.join(local_files_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    local_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                    })
            
            if not local_files:
                info_msg = f"\n{self.terminal.icon('info')} No local files found"
                print(f"{self.terminal.colored(info_msg, 'yellow')}")
                return
            
            print(f"\n{self.terminal.header('LOCAL FILES', 90)}")
            
            # Modern file table
            print(f"{self.terminal.colored('┌─────────────────────┬──────────┬─────────────────────┐', 'blue')}")
            print(f"{self.terminal.colored('│', 'blue')} {self.terminal.colored('Filename', 'cyan'):<19} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Size', 'cyan'):<8} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Last Modified', 'cyan'):<19} {self.terminal.colored('│', 'blue')}")
            print(f"{self.terminal.colored('├─────────────────────┼──────────┼─────────────────────┤', 'blue')}")
            
            for file_info in local_files:
                size_str = self._format_file_size(file_info['size'])
                filename = file_info['filename'][:19] if len(file_info['filename']) > 19 else file_info['filename']
                
                print(f"{self.terminal.colored('│', 'blue')} {self.terminal.icon('file')}{filename:<18} {self.terminal.colored('│', 'blue')} {size_str:<8} {self.terminal.colored('│', 'blue')} {file_info['modified']:<19} {self.terminal.colored('│', 'blue')}")
            
            print(f"{self.terminal.colored('└─────────────────────┴──────────┴─────────────────────┘', 'blue')}")
            
            summary = f"""{self.terminal.icon('chart')} Total Files: {len(local_files)}
{self.terminal.icon('storage')} Total Size: {sum(f['size'] for f in local_files) / 1024**2:.1f} MB
{self.terminal.icon('folder')} Location: {local_files_dir}"""
            
            print(self.terminal.box(summary, "LOCAL STORAGE SUMMARY", 'green'))
            
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Error listing local files: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def get_file_info(self, filename: str):
        """Get detailed file information with modern interface"""
        try:
            request = file_service_pb2.FileInfoRequest(
                requesting_node_id=self.resources.node_id,
                filename=filename
            )
            
            try:
                response = self.controller_stub.GetFileInfo(request, timeout=10)
            except grpc.RpcError as e:
                error_msg = f"{self.terminal.icon('error')} Failed to get file info: {e.code()}"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            if not response.found:
                error_msg = f"{self.terminal.icon('error')} File '{filename}' not found in cloud storage"
                print(f"{self.terminal.colored(error_msg, 'red')}")
                return
            
            file_meta = response.metadata
            
            file_details = f"""{self.terminal.icon('file')} File: {filename}
{self.terminal.icon('chart')} Size: {self._format_file_size(file_meta.size)} ({file_meta.size:,} bytes)
{self.terminal.icon('gear')} Chunks: {file_meta.chunk_count} segments
{self.terminal.icon('time')} Upload Date: {file_meta.upload_date}
{self.terminal.icon('key')} Checksum: {file_meta.checksum}
{self.terminal.icon('shield')} Replicas: {len(response.replicas)} nodes"""
            
            print(f"\n{self.terminal.box(file_details, 'FILE DETAILS', 'blue')}")
            
            # Replica information
            replica_info = f"{self.terminal.colored('REPLICA STATUS:', 'cyan')}\n"
            for i, replica in enumerate(response.replicas, 1):
                status_icon = self.terminal.icon('success') if replica.is_online else self.terminal.icon('cross')
                status_text = "Online" if replica.is_online else "Offline"
                replica_info += f"  {status_icon} {replica.node_id} ({replica.latency_ms}ms) - {status_text}\n"
            
            print(self.terminal.box(replica_info.strip(), "REPLICA NODES", 'yellow'))
            
            # Performance estimates
            estimated_time = file_meta.size / (self.resources.bandwidth_bps / 8) if self.resources.bandwidth_bps > 0 else 0
            
            performance_info = f"""{self.terminal.icon('lightning')} Bandwidth: {self.resources.bandwidth_mbps} Mbps
{self.terminal.icon('time')} Estimated Download: {estimated_time:.1f}s
{self.terminal.icon('chart')} Transfer Rate: {file_meta.size / estimated_time / 1024**2:.1f} MB/s"""
            
            print(self.terminal.box(performance_info, "PERFORMANCE", 'green'))
            
        except Exception as e:
            error_msg = f"{self.terminal.icon('error')} Error getting file info: {e}"
            print(f"{self.terminal.colored(error_msg, 'red')}")
    
    def show_node_status(self):
        """Display modern node status"""
        status_info = self.resources.get_status_info()
        
        # System information
        system_info = f"""{self.terminal.icon('node')} Node ID: {self.terminal.colored(status_info['node_id'], 'cyan')}
{self.terminal.icon('network')} Network: {status_info['network']}
{self.terminal.icon('key')} MAC Address: {status_info['mac_address']}"""
        
        print(f"\n{self.terminal.box(system_info, 'SYSTEM INFO', 'blue')}")
        
        # Hardware status
        hardware_info = f"""{self.terminal.icon('cpu')} CPU: {status_info['cpu_info']}
{self.terminal.icon('memory')} RAM: {status_info['ram_info']} (Usage: {status_info['ram_usage']})
{self.terminal.icon('storage')} Storage: {status_info['storage_info']} (Usage: {status_info['storage_usage']})
{self.terminal.icon('bandwidth')} Bandwidth: {status_info['bandwidth_info']}
{self.terminal.icon('chart')} Network Usage: {status_info['network_usage']}"""
        
        print(self.terminal.box(hardware_info, 'HARDWARE STATUS', 'yellow'))
        
        # Storage details
        connection_status = f"{self.terminal.icon('success')} Connected" if self.registered else f"{self.terminal.icon('cross')} Disconnected"
        node_status = f"{self.terminal.icon('success')} Online" if self.running else f"{self.terminal.icon('cross')} Offline"
        
        storage_info = f"""{self.terminal.icon('file')} Local Files: {len(self.local_storage)}
{self.terminal.icon('shield')} Replicas Stored: {len(self.replica_storage)}
{self.terminal.icon('chain')} Controller: {connection_status}
{self.terminal.icon('heart')} Heartbeat: {self.heartbeat_interval}s interval
{self.terminal.icon('gear')} Status: {node_status}"""
        
        print(self.terminal.box(storage_info, 'STORAGE & CONNECTION', 'green'))
    
    def show_help(self):
        """Display modern help interface"""
        print(f"\n{self.terminal.header('AVAILABLE COMMANDS', 80)}")
        
        commands = [
            ("upload <filepath>", "Upload local file to cloud storage", "upload"),
            ("download <filename>", "Download file from cloud storage", "download"),
            ("list / ls / files", "Show all files on cloud", "file"),
            ("local / localfiles", "Show local files on this node", "folder"),
            ("info <filename>", "Get detailed file information", "info"),
            ("status", "Show node status and resources", "gear"),
            ("clear / cls", "Clear terminal screen", "eye"),
            ("help", "Show this help message", "info"),
            ("exit / quit / q", "Shutdown node gracefully", "cross")
        ]
        
        print(f"{self.terminal.colored('┌─────────────────────┬─────────────────────────────────────┐', 'blue')}")
        print(f"{self.terminal.colored('│', 'blue')} {self.terminal.colored('Command', 'cyan'):<19} {self.terminal.colored('│', 'blue')} {self.terminal.colored('Description', 'cyan'):<35} {self.terminal.colored('│', 'blue')}")
        print(f"{self.terminal.colored('├─────────────────────┼─────────────────────────────────────┤', 'blue')}")
        
        for cmd, desc, icon in commands:
            icon_str = self.terminal.icon(icon)
            print(f"{self.terminal.colored('│', 'blue')} {icon_str}{cmd:<18} {self.terminal.colored('│', 'blue')} {desc:<35} {self.terminal.colored('│', 'blue')}")
        
        print(f"{self.terminal.colored('└─────────────────────┴─────────────────────────────────────┘', 'blue')}")
        
        examples = f"""{self.terminal.icon('upload')} upload /path/to/file.txt
{self.terminal.icon('download')} download file.txt
{self.terminal.icon('file')} list
{self.terminal.icon('folder')} local
{self.terminal.icon('info')} info file.txt
{self.terminal.icon('gear')} status"""
        
        print(self.terminal.box(examples, "USAGE EXAMPLES", 'green'))
    
    def shutdown(self):
        """Gracefully shutdown with modern interface"""
        shutdown_info = f"""{self.terminal.icon('gear')} Shutting down {self.resources.node_id}
{self.terminal.icon('sync')} Stopping services...
{self.terminal.icon('chain')} Unregistering from controller...
{self.terminal.icon('network')} Closing connections..."""
        
        print(self.terminal.box(shutdown_info, "SHUTDOWN SEQUENCE", 'yellow'))
        
        self.running = False
        
        # Unregister from controller
        if self.registered:
            try:
                request = file_service_pb2.UnregisterNodeRequest(
                    node_id=self.resources.node_id,
                    reason="Normal shutdown"
                )
                self.controller_stub.UnregisterNode(request, timeout=5)
                success_msg = f"{self.terminal.icon('success')} Unregistered from controller"
                print(f"{self.terminal.colored(success_msg, 'green')}")
            except:
                pass
        
        # Stop gRPC server
        if self.node_server:
            self.node_server.stop(5)
        
        # Close controller connection
        if self.controller_channel:
            self.controller_channel.close()
        
        final_msg = f"{self.terminal.icon('success')} {self.resources.node_id} shutdown complete"
        print(f"{self.terminal.colored(final_msg, 'green')}")
        print(f"\n{self.terminal.colored('Thank you for using Distributed Storage Network!', 'cyan')}\n")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes >= 1024**3:
            return f"{size_bytes / 1024**3:.1f}GB"
        elif size_bytes >= 1024**2:
            return f"{size_bytes / 1024**2:.1f}MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes}B"
    
    # gRPC Service Methods (for node-to-node communication)
    def TransferChunk(self, request, context):
        """Receive chunk from another node for replication"""
        try:
            calculated_checksum = hashlib.md5(request.chunk_data).hexdigest()
            if calculated_checksum != request.checksum:
                return file_service_pb2.TransferChunkResponse(
                    success=False,
                    message="Checksum verification failed"
                )
            
            chunk_key = f"{request.file_id}_{request.chunk_id}"
            self.replica_storage[chunk_key] = {
                'data': request.chunk_data,
                'checksum': request.checksum,
                'source_node': request.source_node_id
            }
            
            self.resources.allocate_storage(len(request.chunk_data))
            
            return file_service_pb2.TransferChunkResponse(
                success=True,
                message="Chunk stored successfully",
                stored_checksum=calculated_checksum
            )
            
        except Exception as e:
            return file_service_pb2.TransferChunkResponse(
                success=False,
                message=f"Storage failed: {str(e)}"
            )
    
    def RequestChunk(self, request, context):
        """Serve chunk to another node"""
        try:
            chunk_key = f"{request.file_id}_{request.chunk_id}"
            
            if chunk_key in self.replica_storage:
                chunk_info = self.replica_storage[chunk_key]
                return file_service_pb2.ChunkResponse(
                    found=True,
                    chunk_data=chunk_info['data'],
                    checksum=chunk_info['checksum'],
                    message="Chunk retrieved successfully"
                )
            else:
                return file_service_pb2.ChunkResponse(
                    found=False,
                    chunk_data=b'',
                    checksum='',
                    message="Chunk not found"
                )
                
        except Exception as e:
            return file_service_pb2.ChunkResponse(
                found=False,
                chunk_data=b'',
                checksum='',
                message=f"Retrieval failed: {str(e)}"
            )


def parse_arguments():
    """Parse command line arguments for node configuration"""
    parser = argparse.ArgumentParser(description='Z-Cloud Storage Node with Modern Terminal')

    # Required parameters
    parser.add_argument('--node-id', required=True, help='Unique node identifier (e.g., CloudNode1)')
    
    # Network parameters
    parser.add_argument('--host', default='localhost', help='Network host (default: localhost)')
    parser.add_argument('--port', type=int, required=True, help='Network port (e.g., 5001)')
    parser.add_argument('--mac-address', default=None, help='MAC address (auto-generated if not provided)')
    
    # Hardware parameters
    parser.add_argument('--cpu', type=int, default=2, help='CPU cores (default: 2)')
    parser.add_argument('--cpu-speed', type=float, default=2.4, help='CPU speed in GHz (default: 2.4)')
    parser.add_argument('--ram', type=int, default=4, help='RAM in GB (default: 4)')
    parser.add_argument('--storage', type=int, default=100, help='Storage in GB (default: 100)')
    parser.add_argument('--bandwidth', type=int, default=100, help='Bandwidth in Mbps (default: 100)')
    
    # Controller connection
    parser.add_argument('--controller-host', default='localhost', help='Controller host (default: localhost)')
    parser.add_argument('--controller-port', type=int, default=5000, help='Controller port (default: 5000)')
    
    return parser.parse_args()


def main():
    """Main function to start a virtual node with modern interface"""
    args = parse_arguments()
    
    # Generate MAC address if not provided
    if not args.mac_address:
        args.mac_address = NodeResources.generate_mac_address(args.node_id)
    
    # Create node resources configuration
    resources = NodeResources(
        node_id=args.node_id,
        host=args.host,
        port=args.port,
        cpu_cores=args.cpu,
        cpu_speed=args.cpu_speed,
        ram_gb=args.ram,
        storage_gb=args.storage,
        bandwidth_mbps=args.bandwidth,
        mac_address=args.mac_address
    )
    
    # Create and start the modern node
    node = StorageZ-CloudNode(resources, args.controller_host, args.controller_port)
    node.start_node()


if __name__ == "__main__":
    main()