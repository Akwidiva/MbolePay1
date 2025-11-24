import time
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode, TransferStatus

class Cloud:
    def __init__(self):
        self.network = StorageVirtualNetwork()
        self.users = {}  # user_id: {'files': [file_ids]}
        self.files = {}  # file_id: {'user': user_id, 'name': str, 'size': int, 'locations': [node_ids], 'created_at': time}
        self.node_status = {}  # node_id: {'last_heartbeat': time, 'status': 'alive'/'dead'}

    def add_node(self, node: StorageVirtualNode):
        self.network.add_node(node)
        node.cloud = self
        self.node_status[node.node_id] = {'last_heartbeat': time.time(), 'status': 'alive'}

    def connect_nodes(self, node1_id, node2_id, bandwidth):
        self.network.connect_nodes(node1_id, node2_id, bandwidth)

    def register_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {'files': []}

    def upload_file(self, user_id, file_name, file_size):
        if user_id not in self.users:
            return None

        # Find node with enough space
        available_nodes = [node for node in self.network.nodes.values() if node.used_storage + file_size <= node.total_storage]
        if not available_nodes:
            return None

        # Simple selection: first available
        target_node = available_nodes[0]

        # Generate file_id
        file_id = f"{user_id}-{file_name}-{int(time.time())}"

        # Initiate transfer (simulate direct upload)
        transfer = target_node.initiate_file_transfer(file_id, file_name, file_size)
        if transfer:
            # Simulate completion
            for chunk in transfer.chunks:
                chunk.status = TransferStatus.COMPLETED
                chunk.stored_node = target_node.node_id
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = time.time()
            target_node.used_storage += file_size
            target_node.stored_files[file_id] = transfer

            # Update cloud records
            self.files[file_id] = {
                'user': user_id,
                'name': file_name,
                'size': file_size,
                'locations': [target_node.node_id],
                'created_at': time.time()
            }
            self.users[user_id]['files'].append(file_id)
            return file_id
        return None

    def download_file(self, user_id, file_id):
        if file_id not in self.files or self.files[file_id]['user'] != user_id:
            return None

        # Get from primary location
        location = self.files[file_id]['locations'][0]
        node = self.network.nodes[location]
        return node.stored_files.get(file_id)

    def replicate_file(self, file_id, to_node_id):
        if file_id not in self.files or to_node_id not in self.network.nodes:
            return False

        from_node_id = self.files[file_id]['locations'][0]
        if from_node_id == to_node_id:
            return True

        # Check if target node has space
        to_node = self.network.nodes[to_node_id]
        if to_node.used_storage + self.files[file_id]['size'] > to_node.total_storage:
            return False

        # Simulate instant replication (no chunk processing for speed)
        to_node.used_storage += self.files[file_id]['size']
        to_node.stored_files[file_id] = self.network.nodes[from_node_id].stored_files[file_id]
        self.files[file_id]['locations'].append(to_node_id)
        return True

    def receive_heartbeat(self, node_id, storage_stats, network_stats):
        if node_id in self.node_status:
            self.node_status[node_id]['last_heartbeat'] = time.time()
            self.node_status[node_id]['status'] = 'alive'
            # Could log stats or handle

    def get_cloud_stats(self):
        return {
            'total_users': len(self.users),
            'total_files': len(self.files),
            'total_nodes': len(self.network.nodes),
            'network_stats': self.network.get_network_stats()
        }