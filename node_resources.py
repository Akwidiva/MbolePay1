#!/usr/bin/env python3
"""
node_resources.py - Node Configuration and Resource Management

This module defines the NodeResources class that handles hardware and network
specifications for virtual machine nodes in the distributed storage system.
"""

from dataclasses import dataclass
import hashlib
import time


@dataclass
class NodeResources:
    """Node hardware and network resources configuration"""
    node_id: str
    host: str
    port: int
    cpu_cores: int
    cpu_speed: float  # GHz
    ram_gb: int
    storage_gb: int
    bandwidth_mbps: int
    mac_address: str
    
    def __post_init__(self):
        """Convert units to bytes/bits for internal calculations"""
        self.ram_bytes = self.ram_gb * 1024**3
        self.storage_bytes = self.storage_gb * 1024**3
        self.bandwidth_bps = self.bandwidth_mbps * 1024**2
        
        # Initialize usage tracking
        self.ram_used = 0
        self.storage_used = 0
        self.network_utilization = 0.0
        
    def display_config(self):
        """Display node configuration with modern terminal design"""
        print("\n" + "▓" * 70)
        print("▓" + " " * 68 + "▓")
        print("▓" + "🖥️  VIRTUAL MACHINE NODE INITIALIZATION".center(68) + "▓")
        print("▓" + " " * 68 + "▓")
        print("▓" * 70)
        print()
        
        # Node Identity Section
        print("┌─── 🏷️  NODE IDENTITY " + "─" * 45 + "┐")
        print(f"│  🆔 Node ID      : {self.node_id:<35} │")
        print(f"│  📍 MAC Address  : {self.mac_address:<35} │")
        print("└" + "─" * 68 + "┘")
        print()
        
        # Network Configuration
        print("┌─── 🌐 NETWORK CONFIGURATION " + "─" * 37 + "┐")
        print(f"│  🏠 Host         : {self.host:<35} │")
        print(f"│  🔌 Port         : {self.port:<35} │")
        print(f"│  📡 Bandwidth    : {self.bandwidth_mbps} Mbps ({self.bandwidth_bps:,} bytes/sec) │".ljust(69) + "│")
        print("└" + "─" * 68 + "┘")
        print()
        
        # Hardware Resources
        print("┌─── ⚙️  HARDWARE RESOURCES " + "─" * 39 + "┐")
        print(f"│  🔧 CPU          : {self.cpu_cores} cores @ {self.cpu_speed} GHz{'':<20} │")
        print(f"│  🧠 RAM          : {self.ram_gb} GB ({self.ram_bytes:,} bytes){'':<10} │".ljust(69) + "│")
        print(f"│  💾 Storage      : {self.storage_gb} GB ({self.storage_bytes:,} bytes){'':<8} │".ljust(69) + "│")
        print("└" + "─" * 68 + "┘")
        print()
        
        # Status Bar
        print("┌─── 📊 SYSTEM STATUS " + "─" * 44 + "┐")
        print("│  🔄 Initialization Status: READY                           │")
        print(f"│  ⏰ Timestamp: {self.timestamp():<40} │")
        print("└" + "─" * 68 + "┘")
        print("\n" + "▓" * 70 + "\n")
    
    def display_status(self):
        """Display current resource usage with progress bars"""
        print("\n" + "▓" * 70)
        print("▓" + "📈 RESOURCE UTILIZATION MONITOR".center(68) + "▓")
        print("▓" * 70)
        print()
        
        # RAM Usage
        ram_used_gb = self.ram_used / 1024**3
        ram_percent = (ram_used_gb / self.ram_gb) * 100
        ram_bar = self._create_progress_bar(ram_percent)
        print(f"🧠 RAM Usage    : {ram_bar} {ram_used_gb:.1f}/{self.ram_gb} GB ({ram_percent:.1f}%)")
        
        # Storage Usage  
        storage_used_gb = self.storage_used / 1024**3
        storage_percent = (storage_used_gb / self.storage_gb) * 100
        storage_bar = self._create_progress_bar(storage_percent)
        print(f"💾 Storage Usage: {storage_bar} {storage_used_gb:.1f}/{self.storage_gb} GB ({storage_percent:.1f}%)")
        
        # Network Usage
        network_bar = self._create_progress_bar(self.network_utilization)
        print(f"📡 Network Load : {network_bar} {self.network_utilization:.1f}%")
        
        print("\n" + "▓" * 70 + "\n")
    
    def _create_progress_bar(self, percentage, width=30):
        """Create a visual progress bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage < 50:
            color = "🟢"  # Green
        elif percentage < 80:
            color = "🟡"  # Yellow
        else:
            color = "🔴"  # Red
            
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {color}"
    
    def display_compact_info(self):
        """Compact single-line node info"""
        print(f"🖥️  {self.node_id} | 🌐 {self.host}:{self.port} | "
              f"🔧 {self.cpu_cores}C@{self.cpu_speed}GHz | 🧠 {self.ram_gb}GB | 💾 {self.storage_gb}GB")
    
    def get_status_info(self):
        """Return formatted status information"""
        return {
            'node_id': self.node_id,
            'network': f"{self.host}:{self.port}",
            'mac_address': self.mac_address,
            'cpu_info': f"{self.cpu_cores} cores @ {self.cpu_speed} GHz",
            'ram_info': f"{self.ram_gb} GB",
            'storage_info': f"{self.storage_gb} GB", 
            'bandwidth_info': f"{self.bandwidth_mbps} Mbps",
            'ram_usage': f"{self.ram_used / 1024**3:.1f} GB / {self.ram_gb} GB",
            'storage_usage': f"{self.storage_used / 1024**3:.1f} GB / {self.storage_gb} GB",
            'network_usage': f"{self.network_utilization:.1f}%"
        }
    
    def can_store_data(self, size_bytes: int) -> bool:
        """Check if node has enough storage space"""
        return (self.storage_used + size_bytes) <= self.storage_bytes
    
    def allocate_storage(self, size_bytes: int) -> bool:
        """Allocate storage space if available"""
        if self.can_store_data(size_bytes):
            self.storage_used += size_bytes
            return True
        return False
    
    def deallocate_storage(self, size_bytes: int):
        """Free up storage space"""
        self.storage_used = max(0, self.storage_used - size_bytes)
    
    def update_network_utilization(self, utilization_percent: float):
        """Update current network utilization"""
        self.network_utilization = max(0.0, min(100.0, utilization_percent))
    
    @staticmethod
    def generate_mac_address(node_id: str) -> str:
        """Generate MAC address based on node ID"""
        hash_obj = hashlib.md5(node_id.encode())
        hex_str = hash_obj.hexdigest()[:12]
        mac = ':'.join(hex_str[i:i+2].upper() for i in range(0, 12, 2))
        return mac
    
    @staticmethod
    def timestamp() -> str:
        """Get current timestamp"""
        return time.strftime("%Y-%m-%d %H:%M:%S")


# Demo usage
if __name__ == "__main__":
    # Create a sample node
    node = NodeResources(
        node_id="NODE-001",
        host="192.168.1.100",
    port=8081,
        cpu_cores=8,
        cpu_speed=3.2,
        ram_gb=32,
        storage_gb=1000,
        bandwidth_mbps=1000,
        mac_address=NodeResources.generate_mac_address("NODE-001")
    )
    
    # Display configuration
    node.display_config()
    
    # Simulate some usage
    node.allocate_storage(100 * 1024**3)  # 100GB
    node.ram_used = 8 * 1024**3  # 8GB
    node.update_network_utilization(65.0)
    
    # Display status
    node.display_status()
    
    # Display compact info
    print("Compact view:")
    node.display_compact_info()