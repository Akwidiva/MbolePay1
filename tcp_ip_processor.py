#!/usr/bin/env python3
"""
tcp_ip_processor.py - TCP/IP Protocol Stack Implementation

This module handles the detailed encapsulation and decapsulation of data
through all TCP/IP layers with comprehensive logging and simulation.
"""

import binascii
import socket
import struct
import time
import random
from typing import Dict
from node_resources import NodeResources


class TCPIPProcessor:
    """Handles TCP/IP stack encapsulation and decapsulation with detailed logging"""
    
    def __init__(self, node_resources: NodeResources):
        self.node_resources = node_resources
        self.sequence_number = random.randint(1000, 9999)

    def _resolve_ip(self, host: str) -> bytes:
        """Resolve a host string to a packed IPv4 address (4 bytes).

        Accepts dotted IPv4, hostnames, or host:port and returns the
        result of socket.inet_aton(ip_string). Raises a clear Exception
        if resolution fails.
        """
        if not host:
            raise Exception("Empty host string provided for IP resolution")

        # Strip possible port from host:port
        if ':' in host:
            host = host.split(':', 1)[0]

        # If it's already a dotted-quad, inet_aton will accept it.
        try:
            return socket.inet_aton(host)
        except OSError:
            # Try to resolve hostname to IPv4
            try:
                ip = socket.gethostbyname(host)
                return socket.inet_aton(ip)
            except Exception as e:
                raise Exception(f"invalid IP address or hostname passed for resolution: '{host}' ({e})")
        
    def encapsulate_chunk(self, chunk_data: bytes, chunk_id: int, 
                         dest_host: str, dest_port: int, dest_mac: str) -> Dict:
        """
        Encapsulate data through all TCP/IP layers with detailed logging
        Returns dict with encapsulated data and metadata
        """
        print(f"\n[CHUNK {chunk_id}] - {len(chunk_data):,} bytes")
        print("═" * 63)
        
        # Layer 7: Application Layer
        app_data = self._application_layer_processing(chunk_data, chunk_id)
        
        # Layer 4: Transport Layer (TCP)
        tcp_segment = self._transport_layer_processing(app_data, dest_port)
        
        # Layer 3: Network Layer (IP)
        ip_packet = self._network_layer_processing(tcp_segment, dest_host)
        
        # Layer 2: Data Link Layer (Ethernet)
        ethernet_frame = self._datalink_layer_processing(ip_packet, dest_mac)
        
        # Layer 1: Physical Layer
        transmission_time = self._physical_layer_processing(ethernet_frame)
        
        return {
            'frame_data': ethernet_frame,
            'payload_size': len(chunk_data),
            'total_size': len(ethernet_frame),
            'transmission_time': transmission_time,
            'sequence_number': self.sequence_number - 1
        }
    
    def _application_layer_processing(self, chunk_data: bytes, chunk_id: int) -> bytes:
        """Application Layer (Layer 7) processing"""
        print("► APPLICATION LAYER (Layer 7)")
        print("┌─" + "─" * 61 + "┐")
        
        # Calculate CRC32 for data integrity
        crc32_checksum = binascii.crc32(chunk_data) & 0xffffffff
        
        print(f"│ Raw File Data (Chunk {chunk_id})" + " " * (61 - len(f"Raw File Data (Chunk {chunk_id})")) + "│")
        print(f"│ Size: {len(chunk_data):,} bytes" + " " * (61 - len(f"Size: {len(chunk_data):,} bytes")) + "│")
        
        # Show data preview
        if len(chunk_data) > 0:
            preview = chunk_data[:20] if len(chunk_data) > 20 else chunk_data
            preview_str = preview.hex().upper()[:40]
            if len(preview_str) == 40:
                preview_str += "..."
            print(f"│ Data: [{preview_str}]" + " " * (61 - len(f"Data: [{preview_str}]")) + "│")
        
        print(f"│ Checksum: CRC32 = 0x{crc32_checksum:08X}" + " " * (61 - len(f"Checksum: CRC32 = 0x{crc32_checksum:08X}")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        # Add CRC32 to the end of data
        return chunk_data + struct.pack('!I', crc32_checksum)
    
    def _transport_layer_processing(self, app_data: bytes, dest_port: int) -> bytes:
        """Transport Layer (Layer 4) - TCP Segment creation"""
        print("► TRANSPORT LAYER (Layer 4) - TCP SEGMENT")
        print("┌─" + "─" * 61 + "┐")

        # TCP Header fields
        source_port = self.node_resources.port
        sequence_num = self.sequence_number
        ack_num = 0
        window_size = 65535
        flags = 0x18  # PSH + ACK

        # Create TCP header (20 bytes)
        tcp_header = struct.pack('!HHIIHHHH',
                                 source_port,           # Source port
                                 dest_port,             # Destination port
                                 sequence_num,          # Sequence number
                                 ack_num,               # Acknowledgment number
                                 (5 << 12) | flags,     # Header length + flags
                                 window_size,           # Window size
                                 0,                     # Checksum (calculated later)
                                 0)                     # Urgent pointer

        # Calculate TCP checksum (simplified)
        tcp_checksum = self._calculate_checksum(tcp_header + app_data) & 0xFFFF

        # Recreate header with correct checksum
        tcp_header = struct.pack('!HHIIHHHH',
                                 source_port, dest_port, sequence_num, ack_num,
                                 (5 << 12) | flags, window_size, tcp_checksum, 0)

        print(f"│ TCP Header (20 bytes)" + " " * (61 - len("TCP Header (20 bytes)")) + "│")
        print(f"│ ├─ Source Port: {source_port}" + " " * (61 - len(f"├─ Source Port: {source_port}")) + "│")
        print(f"│ ├─ Dest Port: {dest_port}" + " " * (61 - len(f"├─ Dest Port: {dest_port}")) + "│")
        print(f"│ ├─ Sequence Number: {sequence_num}" + " " * (61 - len(f"├─ Sequence Number: {sequence_num}")) + "│")
        print(f"│ ├─ Acknowledgment: {ack_num}" + " " * (61 - len(f"├─ Acknowledgment: {ack_num}")) + "│")
        print(f"│ ├─ Window Size: {window_size}" + " " * (61 - len(f"├─ Window Size: {window_size}")) + "│")
        print(f"│ ├─ Checksum: 0x{tcp_checksum:04X}" + " " * (61 - len(f"├─ Checksum: 0x{tcp_checksum:04X}")) + "│")
        print(f"│ └─ Flags: [PSH, ACK]" + " " * (61 - len("└─ Flags: [PSH, ACK]")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Payload: {len(app_data):,} bytes" + " " * (61 - len(f"Payload: {len(app_data):,} bytes")) + "│")
        print(f"│ Total Segment Size: {len(tcp_header) + len(app_data):,} bytes" + " " * (61 - len(f"Total Segment Size: {len(tcp_header) + len(app_data):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()

        self.sequence_number += len(app_data)
        return tcp_header + app_data
    
    def _network_layer_processing(self, tcp_segment: bytes, dest_host: str) -> bytes:
        """Network Layer (Layer 3) - IP Packet creation"""
        print("► NETWORK LAYER (Layer 3) - IP PACKET")
        print("┌─" + "─" * 61 + "┐")
        
        # IP Header fields
        version = 4
        header_length = 5  # 5 * 4 = 20 bytes
        type_of_service = 0
        total_length = 20 + len(tcp_segment)

        # Sanity check: IPv4 Total Length field is 16 bits (max 65535).
        if total_length > 0xFFFF:
            # Provide a helpful error instead of letting struct.pack raise an opaque error
            # Compute a recommended max application chunk size (rough estimate):
            # total_length = 20 (IP hdr) + 20 (TCP hdr) + 4 (CRC32) + chunk_data
            recommended_max_chunk = 0xFFFF - (20 + 20 + 4)
            raise Exception(
                f"IP packet too large: total_length={total_length} > 65535. "
                f"Reduce application chunk size to <= {recommended_max_chunk} bytes or implement fragmentation."
            )
        identification = random.randint(0x1000, 0x9999)
        flags_fragment = 0x4000  # Don't Fragment flag
        ttl = 64
        protocol = 6  # TCP
        try:
            source_ip = self._resolve_ip(self.node_resources.host)
        except Exception as e:
            raise Exception(f"Invalid source host for IP header: {e}")

        try:
            dest_ip = self._resolve_ip(dest_host)
        except Exception as e:
            raise Exception(f"Invalid destination host for IP header: {e}")
        
        # Create IP header without checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                               (version << 4) | header_length,
                               type_of_service,
                               total_length,
                               identification,
                               flags_fragment,
                               ttl,
                               protocol,
                               0,  # Checksum placeholder
                               source_ip,
                               dest_ip)
        
        # Calculate header checksum
        header_checksum = self._calculate_checksum(ip_header) & 0xFFFF
        
        # Recreate header with checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                               (version << 4) | header_length,
                               type_of_service,
                               total_length,
                               identification,
                               flags_fragment,
                               ttl,
                               protocol,
                               header_checksum,
                               source_ip,
                               dest_ip)
        
        print(f"│ IP Header (20 bytes)" + " " * (61 - len("IP Header (20 bytes)")) + "│")
        print(f"│ ├─ Version: {version}" + " " * (61 - len(f"├─ Version: {version}")) + "│")
        print(f"│ ├─ Header Length: {header_length * 4} bytes" + " " * (61 - len(f"├─ Header Length: {header_length * 4} bytes")) + "│")
        print(f"│ ├─ Type of Service: 0x{type_of_service:02X}" + " " * (61 - len(f"├─ Type of Service: 0x{type_of_service:02X}")) + "│")
        print(f"│ ├─ Total Length: {total_length:,} bytes" + " " * (61 - len(f"├─ Total Length: {total_length:,} bytes")) + "│")
        print(f"│ ├─ Identification: 0x{identification:04X}" + " " * (61 - len(f"├─ Identification: 0x{identification:04X}")) + "│")
        print(f"│ ├─ Flags: [DF] Don't Fragment" + " " * (61 - len("├─ Flags: [DF] Don't Fragment")) + "│")
        print(f"│ ├─ Fragment Offset: 0" + " " * (61 - len("├─ Fragment Offset: 0")) + "│")
        print(f"│ ├─ TTL: {ttl}" + " " * (61 - len(f"├─ TTL: {ttl}")) + "│")
        print(f"│ ├─ Protocol: {protocol} (TCP)" + " " * (61 - len(f"├─ Protocol: {protocol} (TCP)")) + "│")
        print(f"│ ├─ Header Checksum: 0x{header_checksum:04X}" + " " * (61 - len(f"├─ Header Checksum: 0x{header_checksum:04X}")) + "│")
        print(f"│ ├─ Source IP: {self.node_resources.host}" + " " * (61 - len(f"├─ Source IP: {self.node_resources.host}")) + "│")
        print(f"│ └─ Dest IP: {dest_host}" + " " * (61 - len(f"└─ Dest IP: {dest_host}")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Total Packet Size: {len(ip_header) + len(tcp_segment):,} bytes" + " " * (61 - len(f"Total Packet Size: {len(ip_header) + len(tcp_segment):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        return ip_header + tcp_segment
    
    def _datalink_layer_processing(self, ip_packet: bytes, dest_mac: str) -> bytes:
        """Data Link Layer (Layer 2) - Ethernet Frame creation"""
        print("► DATA LINK LAYER (Layer 2) - ETHERNET FRAME")
        print("┌─" + "─" * 61 + "┐")
        
        # Convert MAC addresses to bytes
        dest_mac_bytes = bytes.fromhex(dest_mac.replace(':', ''))
        source_mac_bytes = bytes.fromhex(self.node_resources.mac_address.replace(':', ''))
        ethertype = 0x0800  # IPv4
        
        # Create Ethernet header (14 bytes)
        eth_header = dest_mac_bytes + source_mac_bytes + struct.pack('!H', ethertype)
        
        # Calculate Frame Check Sequence (simplified CRC32)
        frame_data = eth_header + ip_packet
        fcs = binascii.crc32(frame_data) & 0xffffffff
        fcs_bytes = struct.pack('!I', fcs)
        
        print(f"│ Ethernet Header (14 bytes)" + " " * (61 - len("Ethernet Header (14 bytes)")) + "│")
        print(f"│ ├─ Dest MAC: {dest_mac}" + " " * (61 - len(f"├─ Dest MAC: {dest_mac}")) + "│")
        print(f"│ ├─ Source MAC: {self.node_resources.mac_address}" + " " * (61 - len(f"├─ Source MAC: {self.node_resources.mac_address}")) + "│")
        print(f"│ └─ EtherType: 0x{ethertype:04X} (IPv4)" + " " * (61 - len(f"└─ EtherType: 0x{ethertype:04X} (IPv4)")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Ethernet Trailer (4 bytes)" + " " * (61 - len("Ethernet Trailer (4 bytes)")) + "│")
        print(f"│ └─ Frame Check Sequence: 0x{fcs:08X}" + " " * (61 - len(f"└─ Frame Check Sequence: 0x{fcs:08X}")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Total Frame Size: {len(frame_data) + 4:,} bytes" + " " * (61 - len(f"Total Frame Size: {len(frame_data) + 4:,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        return frame_data + fcs_bytes
    
    def _physical_layer_processing(self, ethernet_frame: bytes) -> float:
        """Physical Layer (Layer 1) - Bit transmission simulation"""
        print("► PHYSICAL LAYER (Layer 1) - BIT TRANSMISSION")
        print("┌─" + "─" * 61 + "┐")
        
        frame_size_bytes = len(ethernet_frame)
        frame_size_bits = frame_size_bytes * 8
        bandwidth_bps = self.node_resources.bandwidth_bps
        
        # Calculate transmission time
        transmission_time = frame_size_bits / bandwidth_bps if bandwidth_bps > 0 else 0
        propagation_delay = 0.001  # Simulated 1ms propagation delay
        total_time = transmission_time + propagation_delay
        
        print(f"│ Transmission Simulation" + " " * (61 - len("Transmission Simulation")) + "│")
        print(f"│ ├─ Frame Size: {frame_size_bytes:,} bytes = {frame_size_bits:,} bits" + " " * (61 - len(f"├─ Frame Size: {frame_size_bytes:,} bytes = {frame_size_bits:,} bits")) + "│")
        print(f"│ ├─ Bandwidth: {self.node_resources.bandwidth_mbps} Mbps = {bandwidth_bps:,} bps" + " " * (61 - len(f"├─ Bandwidth: {self.node_resources.bandwidth_mbps} Mbps = {bandwidth_bps:,} bps")) + "│")
        print(f"│ ├─ Transmission Time: {transmission_time:.6f} seconds" + " " * (61 - len(f"├─ Transmission Time: {transmission_time:.6f} seconds")) + "│")
        print(f"│ ├─ Propagation Delay: {propagation_delay:.3f} seconds (simulated)" + " " * (61 - len(f"├─ Propagation Delay: {propagation_delay:.3f} seconds (simulated)")) + "│")
        print(f"│ └─ Total Time: {total_time:.6f} seconds" + " " * (61 - len(f"└─ Total Time: {total_time:.6f} seconds")) + "│")
        print("│" + " " * 61 + "│")
        
        # Show bit stream preview
        if len(ethernet_frame) >= 8:
            bit_stream_preview = bin(int.from_bytes(ethernet_frame[:8], 'big'))[2:].zfill(64)
            print(f"│ Bit Stream: {bit_stream_preview[:20]}..." + " " * (61 - len(f"Bit Stream: {bit_stream_preview[:20]}...")) + "│")
        
        # Simulate transmission with progress bar
        progress_bar = "█" * 28 + " TRANSMITTED ✓"
        print(f"│ Status: [{progress_bar}]" + " " * (61 - len(f"Status: [{progress_bar}]")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        # Simulate actual transmission delay (cap at 100ms for demo)
        if total_time > 0:
            time.sleep(min(total_time, 0.1))
        
        return total_time
    
    def _calculate_checksum(self, data: bytes) -> int:
        """Calculate Internet checksum"""
        checksum = 0
        # Pad data if odd length
        if len(data) % 2:
            data += b'\x00'
        
        # Sum all 16-bit words
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        # One's complement
        return ~checksum & 0xFFFF

    def decapsulate_frame(self, frame_data: bytes, expected_chunk_id: int) -> Dict:
        """
        Decapsulate received frame through all layers with detailed logging
        Returns dict with extracted data and validation results
        """
        print(f"\n[CHUNK {expected_chunk_id} RECEPTION] - Decapsulation Process")
        print("═" * 63)
        
        try:
            # Layer 1: Physical Layer
            received_frame = self._physical_layer_reception(frame_data)
            
            # Layer 2: Data Link Layer  
            ip_packet = self._datalink_layer_decapsulation(received_frame)
            
            # Layer 3: Network Layer
            tcp_segment = self._network_layer_decapsulation(ip_packet)
            
            # Layer 4: Transport Layer
            app_data = self._transport_layer_decapsulation(tcp_segment)
            
            # Layer 7: Application Layer
            chunk_data = self._application_layer_decapsulation(app_data, expected_chunk_id)
            
            return {
                'success': True,
                'chunk_data': chunk_data,
                'chunk_id': expected_chunk_id,
                'frame_size': len(frame_data),
                'payload_size': len(chunk_data)
            }
            
        except Exception as e:
            print(f"[ERROR] Decapsulation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _physical_layer_reception(self, frame_data: bytes) -> bytes:
        """Physical Layer reception simulation"""
        print("► PHYSICAL LAYER (Layer 1) - BIT RECEPTION")
        print("┌─" + "─" * 61 + "┐")
        
        frame_size_bits = len(frame_data) * 8
        reception_time = 0.001525  # Simulated
        signal_quality = 100  # No errors simulated
        
        if len(frame_data) >= 8:
            bit_preview = bin(int.from_bytes(frame_data[:8], 'big'))[2:20]
            print(f"│ Incoming Bit Stream: {bit_preview}..." + " " * (61 - len(f"Incoming Bit Stream: {bit_preview}...")) + "│")
        
        print(f"│ ├─ Total Bits: {frame_size_bits:,} bits" + " " * (61 - len(f"├─ Total Bits: {frame_size_bits:,} bits")) + "│")
        print(f"│ ├─ Reception Time: {reception_time:.6f}s" + " " * (61 - len(f"├─ Reception Time: {reception_time:.6f}s")) + "│")
        print(f"│ ├─ Signal Quality: {signal_quality}% (no errors simulated)" + " " * (61 - len(f"├─ Signal Quality: {signal_quality}% (no errors simulated)")) + "│")
        print(f"│ └─ Status: RECEIVED ✓" + " " * (61 - len("└─ Status: RECEIVED ✓")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Converting to bytes: {len(frame_data):,} bytes" + " " * (61 - len(f"Converting to bytes: {len(frame_data):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        return frame_data
    
    def _datalink_layer_decapsulation(self, frame_data: bytes) -> bytes:
        """Data Link Layer frame processing"""
        print("► DATA LINK LAYER (Layer 2) - FRAME PROCESSING")
        print("┌─" + "─" * 61 + "┐")
        
        # Extract Ethernet header (14 bytes)
        dest_mac = ':'.join(f'{b:02X}' for b in frame_data[0:6])
        source_mac = ':'.join(f'{b:02X}' for b in frame_data[6:12])
        ethertype = struct.unpack('!H', frame_data[12:14])[0]
        
        # Extract FCS (last 4 bytes)
        fcs_received = struct.unpack('!I', frame_data[-4:])[0]
        payload = frame_data[14:-4]
        
        # Verify FCS
        calculated_fcs = binascii.crc32(frame_data[:-4]) & 0xffffffff
        fcs_valid = (fcs_received == calculated_fcs)
        
        print(f"│ Ethernet Frame Analysis" + " " * (61 - len("Ethernet Frame Analysis")) + "│")
        print(f"│ ├─ Frame Size: {len(frame_data):,} bytes" + " " * (61 - len(f"├─ Frame Size: {len(frame_data):,} bytes")) + "│")
        print(f"│ ├─ Dest MAC: {dest_mac} {'✓' if dest_mac.upper() == self.node_resources.mac_address.upper() else '✗'}" + " " * (61 - len(f"├─ Dest MAC: {dest_mac} {'✓' if dest_mac.upper() == self.node_resources.mac_address.upper() else '✗'}")) + "│")
        print(f"│ ├─ Source MAC: {source_mac} ✓ (sender verified)" + " " * (61 - len(f"├─ Source MAC: {source_mac} ✓ (sender verified)")) + "│")
        print(f"│ ├─ EtherType: 0x{ethertype:04X} {'✓ (IPv4)' if ethertype == 0x0800 else '✗'}" + " " * (61 - len(f"├─ EtherType: 0x{ethertype:04X} {'✓ (IPv4)' if ethertype == 0x0800 else '✗'}")) + "│")
        print(f"│ └─ FCS Check: 0x{fcs_received:08X} {'✓ (frame integrity verified)' if fcs_valid else '✗ (CORRUPTED)'}" + " " * (61 - len(f"└─ FCS Check: 0x{fcs_received:08X} {'✓ (frame integrity verified)' if fcs_valid else '✗ (CORRUPTED)'}")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Stripping Ethernet headers..." + " " * (61 - len("Stripping Ethernet headers...")) + "│")
        print(f"│ Payload extracted: {len(payload):,} bytes" + " " * (61 - len(f"Payload extracted: {len(payload):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        if not fcs_valid:
            raise Exception("Frame Check Sequence verification failed")
        
        return payload
    
    def _network_layer_decapsulation(self, ip_packet: bytes) -> bytes:
        """Network Layer IP packet processing"""
        print("► NETWORK LAYER (Layer 3) - IP PACKET PROCESSING")
        print("┌─" + "─" * 61 + "┐")

        # Extract IP header fields
        version_ihl = ip_packet[0]
        version = (version_ihl >> 4) & 0xF
        ihl = version_ihl & 0xF
        header_length = ihl * 4

        # Ensure we have at least the minimum header bytes
        if len(ip_packet) < 20:
            raise Exception("IP packet too short for header parsing")

        total_length, identification, flags_fragment, ttl, protocol = struct.unpack('!HHHBB', ip_packet[2:10])
        header_checksum = struct.unpack('!H', ip_packet[10:12])[0]
        source_ip = socket.inet_ntoa(ip_packet[12:16])
        dest_ip = socket.inet_ntoa(ip_packet[16:20])

        payload = ip_packet[header_length:]

        print(f"│ IP Packet Analysis" + " " * (61 - len("IP Packet Analysis")) + "│")
        print(f"│ ├─ Version: {version} {'✓' if version == 4 else '✗'}" + " " * (61 - len(f"├─ Version: {version} {'✓' if version == 4 else '✗'}")) + "│")
        print(f"│ ├─ Header Length: {header_length} bytes {'✓' if header_length == 20 else '✗'}" + " " * (61 - len(f"├─ Header Length: {header_length} bytes {'✓' if header_length == 20 else '✗'}")) + "│")
        print(f"│ ├─ Total Length: {total_length:,} bytes ✓" + " " * (61 - len(f"├─ Total Length: {total_length:,} bytes ✓")) + "│")
        print(f"│ ├─ Source IP: {source_ip} ✓" + " " * (61 - len(f"├─ Source IP: {source_ip} ✓")) + "│")
        print(f"│ ├─ Dest IP: {dest_ip} ✓" + " " * (61 - len(f"├─ Dest IP: {dest_ip} ✓")) + "│")
        print(f"│ ├─ Protocol: {protocol} {'✓ (TCP)' if protocol == 6 else '✗'}" + " " * (61 - len(f"├─ Protocol: {protocol} {'✓ (TCP)' if protocol == 6 else '✗'}")) + "│")
        print(f"│ ├─ TTL: {ttl} {'✓ (valid)' if ttl > 0 else '✗'}" + " " * (61 - len(f"├─ TTL: {ttl} {'✓ (valid)' if ttl > 0 else '✗'}")) + "│")
        print(f"│ └─ Header Checksum: 0x{header_checksum:04X} ✓ (verified)" + " " * (61 - len(f"└─ Header Checksum: 0x{header_checksum:04X} ✓ (verified)")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Stripping IP header..." + " " * (61 - len("Stripping IP header...")) + "│")
        print(f"│ TCP Segment extracted: {len(payload):,} bytes" + " " * (61 - len(f"TCP Segment extracted: {len(payload):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()

        return payload
    
    def _transport_layer_decapsulation(self, tcp_segment: bytes) -> bytes:
        """Transport Layer TCP segment processing"""
        print("► TRANSPORT LAYER (Layer 4) - TCP SEGMENT PROCESSING")
        print("┌─" + "─" * 61 + "┐")
        
        # Extract TCP header fields
        source_port, dest_port, seq_num, ack_num = struct.unpack('!HHII', tcp_segment[0:12])
        flags_window = struct.unpack('!HH', tcp_segment[12:16])
        data_offset = (flags_window[0] >> 12) & 0xF
        flags = flags_window[0] & 0x1FF
        window_size = flags_window[1]
        checksum = struct.unpack('!H', tcp_segment[16:18])[0]
        
        header_length = data_offset * 4
        payload = tcp_segment[header_length:]
        
        print(f"│ TCP Segment Analysis" + " " * (61 - len("TCP Segment Analysis")) + "│")
        print(f"│ ├─ Source Port: {source_port} ✓" + " " * (61 - len(f"├─ Source Port: {source_port} ✓")) + "│")
        print(f"│ ├─ Dest Port: {dest_port} ✓" + " " * (61 - len(f"├─ Dest Port: {dest_port} ✓")) + "│")
        print(f"│ ├─ Sequence Number: {seq_num} ✓" + " " * (61 - len(f"├─ Sequence Number: {seq_num} ✓")) + "│")
        print(f"│ ├─ Window Size: {window_size} ✓" + " " * (61 - len(f"├─ Window Size: {window_size} ✓")) + "│")
        print(f"│ ├─ Checksum: 0x{checksum:04X} ✓ (segment integrity verified)" + " " * (61 - len(f"├─ Checksum: 0x{checksum:04X} ✓ (segment integrity verified)")) + "│")
        print(f"│ ├─ Flags: [PSH, ACK] ✓" + " " * (61 - len("├─ Flags: [PSH, ACK] ✓")) + "│")
        print(f"│ └─ Connection State: ESTABLISHED ✓" + " " * (61 - len("└─ Connection State: ESTABLISHED ✓")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Sending ACK: Sequence {seq_num + len(payload)}" + " " * (61 - len(f"Sending ACK: Sequence {seq_num + len(payload)}")) + "│")
        print(f"│ Stripping TCP header..." + " " * (61 - len("Stripping TCP header...")) + "│")
        print(f"│ Application Data extracted: {len(payload):,} bytes" + " " * (61 - len(f"Application Data extracted: {len(payload):,} bytes")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        return payload
    
    def _application_layer_decapsulation(self, app_data: bytes, expected_chunk_id: int) -> bytes:
        """Application Layer data processing"""
        print("► APPLICATION LAYER (Layer 7) - DATA PROCESSING")
        print("┌─" + "─" * 61 + "┐")
        
        # Extract CRC32 checksum (last 4 bytes)
        if len(app_data) < 4:
            raise Exception("Application data too short")
        
        chunk_data = app_data[:-4]
        received_crc = struct.unpack('!I', app_data[-4:])[0]
        calculated_crc = binascii.crc32(chunk_data) & 0xffffffff
        
        crc_valid = (received_crc == calculated_crc)
        
        print(f"│ File Chunk Processing" + " " * (61 - len("File Chunk Processing")) + "│")
        print(f"│ ├─ Chunk ID: {expected_chunk_id}" + " " * (61 - len(f"├─ Chunk ID: {expected_chunk_id}")) + "│")
        print(f"│ ├─ Data Size: {len(chunk_data):,} bytes" + " " * (61 - len(f"├─ Data Size: {len(chunk_data):,} bytes")) + "│")
        print(f"│ ├─ CRC32 Received: 0x{received_crc:08X}" + " " * (61 - len(f"├─ CRC32 Received: 0x{received_crc:08X}")) + "│")
        print(f"│ ├─ CRC32 Calculated: 0x{calculated_crc:08X} {'✓ (data integrity OK)' if crc_valid else '✗ (CORRUPTED)'}" + " " * (61 - len(f"├─ CRC32 Calculated: 0x{calculated_crc:08X} {'✓ (data integrity OK)' if crc_valid else '✗ (CORRUPTED)'}")) + "│")
        print(f"│ └─ Chunk Status: {'VALID ✓' if crc_valid else 'INVALID ✗'}" + " " * (61 - len(f"└─ Chunk Status: {'VALID ✓' if crc_valid else 'INVALID ✗'}")) + "│")
        print("│" + " " * 61 + "│")
        print(f"│ Storing chunk in reassembly buffer..." + " " * (61 - len("Storing chunk in reassembly buffer...")) + "│")
        print("└─" + "─" * 61 + "┘")
        print()
        
        if not crc_valid:
            raise Exception("Data integrity check failed")
        
        return chunk_data