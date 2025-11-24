from cloud import Cloud
from storage_virtual_node import StorageVirtualNode
import time

# Create cloud
cloud = Cloud()

# Create nodes
node1 = StorageVirtualNode("node1", cpu_capacity=4, memory_capacity=16, storage_capacity=500, bandwidth=1000)
node2 = StorageVirtualNode("node2", cpu_capacity=8, memory_capacity=32, storage_capacity=1000, bandwidth=2000)
node3 = StorageVirtualNode("node3", cpu_capacity=2, memory_capacity=8, storage_capacity=200, bandwidth=500)

# Add nodes to cloud
cloud.add_node(node1)
cloud.add_node(node2)
cloud.add_node(node3)

# Connect nodes
cloud.connect_nodes("node1", "node2", bandwidth=1000)
cloud.connect_nodes("node2", "node3", bandwidth=500)

# Register users
cloud.register_user("user1")
cloud.register_user("user2")

# Upload files
file1 = cloud.upload_file("user1", "document.pdf", 50 * 1024 * 1024)  # 50MB
file2 = cloud.upload_file("user2", "video.mp4", 200 * 1024 * 1024)  # 200MB

print(f"Uploaded file1: {file1}")
print(f"Uploaded file2: {file2}")

# Download
downloaded = cloud.download_file("user1", file1)
if downloaded:
    print(f"Downloaded: {downloaded.file_name}, size: {downloaded.total_size}")

# Replicate file
cloud.replicate_file(file1, "node3")
print(f"Replicated {file1} to node3")

# Get stats
stats = cloud.get_cloud_stats()
print(f"Cloud stats: {stats}")

# Let heartbeats run
time.sleep(35)  # Wait for heartbeats
print("Heartbeats sent")