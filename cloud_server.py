import socket
import threading
import json
import time
from cloud import Cloud

class CloudServer:
    def __init__(self):
        self.cloud = Cloud()
        self.node_sockets = {}  # node_id: socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(5)
        print("Cloud server listening on port 12345")

    def handle_client(self, client_socket, addr):
        node_id = None
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                msg = json.loads(data)
                response = self.process_message(msg, client_socket)
                if response is not None:
                    client_socket.send(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            if node_id:
                if node_id in self.node_sockets:
                    del self.node_sockets[node_id]
                if node_id in self.cloud.node_status:
                    self.cloud.node_status[node_id]['status'] = 'disconnected'
            client_socket.close()

    def process_message(self, msg, client_socket):
        msg_type = msg.get('type')
        if msg_type == 'register_node':
            node_id = msg['node_id']
            cpu = msg['cpu']
            mem = msg['mem']
            stor = msg['stor']
            bw = msg['bw']
            port = msg['port']  # Node's listening port

            from storage_virtual_node import StorageVirtualNode
            node = StorageVirtualNode(node_id, cpu, mem, stor, bw)
            self.cloud.add_node(node)
            self.node_sockets[node_id] = client_socket
            node.cloud = self.cloud  # For heartbeats, but since network, maybe not needed
            print(f"Node {node_id} registered")
            return {'status': 'registered'}

        elif msg_type == 'heartbeat':
            node_id = msg['node_id']
            self.cloud.receive_heartbeat(node_id, msg.get('storage', {}), msg.get('network', {}))
            return None  # No response needed for heartbeats

        elif msg_type == 'upload_file':
            user_id = msg['user_id']
            file_name = msg['file_name']
            file_size = msg['file_size']
            file_id = self.cloud.upload_file(user_id, file_name, file_size)
            return {'file_id': file_id}

        elif msg_type == 'download_file':
            user_id = msg['user_id']
            file_id = msg['file_id']
            transfer = self.cloud.download_file(user_id, file_id)
            if transfer:
                return {'file_name': transfer.file_name, 'size': transfer.total_size}
            return {'error': 'File not found'}

        elif msg_type == 'transfer_file':
            file_id = msg['file_id']
            from_node = msg['from_node']
            to_node = msg['to_node']
            # Initiate transfer
            if self.cloud.replicate_file(file_id, to_node):
                return {'status': 'transfer_initiated'}
            return {'error': 'Transfer failed'}

        elif msg_type == 'list_files':
            user_id = msg['user_id']
            if user_id in self.cloud.users:
                files = list(self.cloud.users[user_id]['files'])
                return {'files': files}
            return {'files': []}

        return {'error': 'Unknown message type'}

    def command_loop(self):
        while True:
            cmd = input("Cloud> ")
            if cmd.startswith('register_user '):
                user_id = cmd.split()[1]
                self.cloud.register_user(user_id)
                print(f"User {user_id} registered")
            elif cmd.startswith('connect '):
                parts = cmd.split()
                node1 = parts[1]
                node2 = parts[2]
                bw = int(parts[3])
                self.cloud.connect_nodes(node1, node2, bw)
                print(f"Connected {node1} to {node2} with {bw} Mbps")
            elif cmd.startswith('stats'):
                stats = self.cloud.get_cloud_stats()
                print(json.dumps(stats, indent=2))
            elif cmd.startswith('nodes'):
                for node_id, status in self.cloud.node_status.items():
                    print(f"{node_id}: {status}")
            elif cmd == 'quit':
                break

    def run(self):
        threading.Thread(target=self.command_loop, daemon=True).start()
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()

if __name__ == '__main__':
    server = CloudServer()
    server.run()