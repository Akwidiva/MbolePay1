import socket
import json
import time
import threading

class NodeClient:
    def __init__(self, node_id, cpu, mem, stor, bw):
        self.node_id = node_id
        self.cpu = cpu
        self.mem = mem
        self.stor = stor
        self.bw = bw
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect_to_cloud(self):
        try:
            self.sock.connect(('localhost', 12345))
            # Register
            msg = {
                'type': 'register_node',
                'node_id': self.node_id,
                'cpu': self.cpu,
                'mem': self.mem,
                'stor': self.stor,
                'bw': self.bw,
                'port': 0  # Not used yet
            }
            self.sock.send(json.dumps(msg).encode())
            response = json.loads(self.sock.recv(1024).decode())
            if response.get('status') == 'registered':
                self.connected = True
                print(f"Node {self.node_id} connected to cloud")
                return True
        except Exception as e:
            print(f"Failed to connect: {e}")
        return False

    def send_heartbeat(self):
        while self.connected:
            try:
                msg = {'type': 'heartbeat', 'node_id': self.node_id}
                self.sock.send(json.dumps(msg).encode())
                time.sleep(30)
            except:
                self.connected = False
                break

    def upload_file(self, user_id, file_name, file_size):
        msg = {
            'type': 'upload_file',
            'user_id': user_id,
            'file_name': file_name,
            'file_size': file_size
        }
        self.sock.send(json.dumps(msg).encode())
        response = json.loads(self.sock.recv(1024).decode())
        return response.get('file_id')

    def download_file(self, user_id, file_id):
        msg = {
            'type': 'download_file',
            'user_id': user_id,
            'file_id': file_id
        }
        self.sock.send(json.dumps(msg).encode())
        response = json.loads(self.sock.recv(1024).decode())
        return response

    def transfer_file(self, file_id, to_node):
        msg = {
            'type': 'transfer_file',
            'file_id': file_id,
            'from_node': self.node_id,
            'to_node': to_node
        }
        self.sock.send(json.dumps(msg).encode())
        response = json.loads(self.sock.recv(1024).decode())
        return response

    def command_loop(self):
        while self.connected:
            cmd = input(f"Node {self.node_id}> ")
            if cmd.startswith('upload '):
                parts = cmd.split()
                if len(parts) != 4:
                    print("Usage: upload <user_id> <file_name> <file_size>")
                    continue
                user_id = parts[1]
                file_name = parts[2]
                file_size = int(parts[3])
                file_id = self.upload_file(user_id, file_name, file_size)
                print(f"Uploaded file: {file_id}")
            elif cmd.startswith('download '):
                parts = cmd.split()
                if len(parts) != 3:
                    print("Usage: download <user_id> <file_id>")
                    continue
                user_id = parts[1]
                file_id = parts[2]
                result = self.download_file(user_id, file_id)
                print(f"Downloaded: {result}")
            elif cmd.startswith('transfer '):
                parts = cmd.split()
                if len(parts) != 3:
                    print("Usage: transfer <file_id> <to_node>")
                    continue
                file_id = parts[1]
                to_node = parts[2]
                result = self.transfer_file(file_id, to_node)
                print(f"Transfer: {result}")
            elif cmd.startswith('list_files '):
                parts = cmd.split()
                if len(parts) != 2:
                    print("Usage: list_files <user_id>")
                    continue
                user_id = parts[1]
                msg = {'type': 'list_files', 'user_id': user_id}
                self.sock.send(json.dumps(msg).encode())
                response = json.loads(self.sock.recv(1024).decode())
                print("Files:", response['files'])
            elif cmd == 'quit':
                self.connected = False
                break

    def run(self):
        if self.connect_to_cloud():
            threading.Thread(target=self.send_heartbeat, daemon=True).start()
            self.command_loop()
        self.sock.close()

if __name__ == '__main__':
    node_id = input("Node ID: ")
    cpu = int(input("CPU cores: "))
    mem = int(input("Memory GB: "))
    stor = int(input("Storage GB: "))
    bw = int(input("Bandwidth Mbps: "))

    client = NodeClient(node_id, cpu, mem, stor, bw)
    client.run()