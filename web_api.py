#!/usr/bin/env python3
"""
web_api.py - Flask Web API for Z-Cloud

This module provides a REST API interface for the Z-Cloud distributed storage system,
allowing web-based interaction with the distributed file system.
"""

import os
import json
import grpc
import hashlib
import tempfile
import socket
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_file, render_template_string, session
from flask_cors import CORS
from flask_session import Session
from werkzeug.utils import secure_filename
import file_service_pb2
import file_service_pb2_grpc
from user_manager import UserManager

app = Flask(__name__, static_folder='static', static_url_path='/static', instance_relative_config=False)
CORS(app)  # Enable CORS for all routes

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'Z-Cloud-secret-key-change-in-production'
Session(app)

# Configuration
CONTROLLER_HOST = 'localhost'
CONTROLLER_PORT = 5000
UPLOAD_FOLDER = 'web_uploads'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# OTP Configuration
OTP_STORAGE = {}  # In-memory OTP storage: {email: {'code': '123456', 'expiry': datetime, 'attempts': 0}}
MAX_OTP_ATTEMPTS = 5
OTP_EXPIRY_MINUTES = 5

# Email Configuration (Update with your email service)
EMAIL_CONFIG = {
    'sender_email': 'akwifonguhjoy@gmail.com',
    'sender_password': os.getenv('EMAIL_PASSWORD', 'wxnjrjiichlqzswh'),  # Get from environment variable, fallback to app password
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(email, otp):
    """Send OTP code via email"""
    try:
        # Get password from EMAIL_CONFIG which reads from environment variable
        password = EMAIL_CONFIG.get('sender_password', '')
        
        if not password:
            # If no password, just print to console for testing
            print(f"\n{'='*60}")
            print(f"OTP for {email}: {otp}")
            print(f"Valid for {OTP_EXPIRY_MINUTES} minutes")
            print(f"(To use real email, set EMAIL_PASSWORD environment variable)")
            print(f"{'='*60}\n")
            return True
        
        # Email content
        subject = "Z-Cloud - Your One-Time Password (OTP)"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1A73E8 0%, #1557B0 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">☁️ Z-Cloud</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Distributed Cloud Storage</p>
            </div>

            <div style="background: white; border: 1px solid #E3E3E3; border-radius: 0 0 10px 10px; padding: 30px;">
                <h2 style="color: #202124; margin-top: 0;">Your Login Verification Code</h2>

                <p style="color: #5F6368; line-height: 1.6;">Hello,</p>
                
                <p style="color: #5F6368; line-height: 1.6;">You requested a verification code for your Z-Cloud account. Please use the code below to complete your login:</p>

                <div style="background: #F8F9FA; border: 2px solid #34A853; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h3 style="margin: 0; color: #202124; font-size: 16px;">Your OTP Code</h3>
                    <div style="font-size: 48px; font-weight: bold; color: #34A853; letter-spacing: 8px; margin: 15px 0;">{otp}</div>
                    <p style="margin: 10px 0 0 0; color: #9AA0A6; font-size: 14px;">Valid for {OTP_EXPIRY_MINUTES} minutes</p>
                </div>

                <div style="background: #FFF3CD; border-left: 4px solid #FBBC04; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>⚠️ Security Notice:</strong> Never share this code with anyone. Z-Cloud support will never ask for this code.
                    </p>
                </div>

                <p style="color: #5F6368; line-height: 1.6; margin-top: 20px;">If you didn't request this code, please ignore this email and your account will remain secure.</p>

                <hr style="border: none; border-top: 1px solid #E3E3E3; margin: 30px 0;">

                <p style="color: #9AA0A6; font-size: 12px; margin: 0;">
                    This email was sent by Z-Cloud System<br>
                    © 2025 Z-Cloud. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = email
        msg['Subject'] = subject
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Send email via SMTP
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], password)
            server.send_message(msg)
        
        print(f"[SUCCESS] OTP email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"[ERROR] Email authentication failed. Check EMAIL_PASSWORD environment variable.")
        print(f"OTP for {email}: {otp} (printed to console as backup)")
        return True  # Still return True so registration continues
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email: {e}")
        print(f"OTP for {email}: {otp} (printed to console as backup)")
        return True  # Still return True so registration continues


# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_node_online(host, port, timeout=2):
    """Check if a node is online by testing port connectivity"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

class WebAPIClient:
    """Client to interact with the gRPC network controller"""
    
    def __init__(self, host=CONTROLLER_HOST, port=CONTROLLER_PORT):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.connect()
    
    def connect(self):
        """Establish connection to the network controller"""
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            self.stub = file_service_pb2_grpc.FileServiceStub(self.channel)
            # Connection established, actual connectivity will be tested in is_connected()
        except Exception as e:
            print(f"Failed to connect to controller: {e}")
            self.channel = None
            self.stub = None
    
    def is_connected(self):
        """Check if connected to controller"""
        if self.channel is None or self.stub is None:
            return False
        
        # Test actual connectivity by checking if controller port is open
        return check_node_online(self.host, self.port, timeout=1)
    
    def reconnect_if_needed(self):
        """Reconnect if connection is lost"""
        if not self.is_connected():
            self.connect()

# Global API client
api_client = WebAPIClient()

# Global user manager
user_manager = UserManager()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/login')
def login():
    """Serve the login page"""
    try:
        with open('static/login.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Login page not found. Please ensure static/login.html exists.", 404

@app.route('/register')
def register():
    """Serve the registration page"""
    try:
        with open('static/register.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Registration page not found. Please ensure static/register.html exists.", 404

@app.route('/reset')
def reset():
    """Serve the password reset page"""
    try:
        with open('static/reset.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Password reset page not found. Please ensure static/reset.html exists.", 404

@app.route('/dashboard')
def dashboard():
    """Interactive dashboard"""
    try:
        with open('static/dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to index.html if dashboard.html doesn't exist
        try:
            with open('static/index.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Dashboard not found. Please ensure static/dashboard.html exists.", 404

@app.route('/')
def index():
    """Main page with API documentation"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Z-Cloud Web API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
            .method { font-weight: bold; color: #e74c3c; }
            .path { font-family: monospace; background: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            .status { padding: 10px; border-radius: 5px; margin: 20px 0; }
            .connected { background: #d5f4e6; border: 1px solid #27ae60; color: #27ae60; }
            .disconnected { background: #fadbd8; border: 1px solid #e74c3c; color: #e74c3c; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Z-Cloud Web API</h1>
            
            <div class="status {{ 'connected' if connected else 'disconnected' }}">
                <strong>Controller Status:</strong> {{ 'Connected' if connected else 'Disconnected' }} 
                ({{ controller_host }}:{{ controller_port }})
            </div>
            
            <h2>📋 Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/status</span><br>
                Get API and controller connection status
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/nodes</span><br>
                List all registered nodes and their status
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/nodes</span><br>
                Create a new Z-Cloud node<br>
                <strong>JSON body:</strong> <code>{"node_id": "CloudNode4", "host": "localhost", "port": 8084, "cpu_cores": 4, "cpu_speed": 2.5, "ram_gb": 8, "storage_gb": 500, "bandwidth_mbps": 100}</code>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/nodes/{node_id}/start</span><br>
                Start a created Z-Cloud node
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/files</span><br>
                List all files in cloud storage<br>
                <strong>Query params:</strong> <code>node_id</code> (optional) - filter files visible to specific node
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/files/{file_id}</span><br>
                Get detailed information about a specific file
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/upload</span><br>
                Upload a file to cloud storage<br>
                <strong>Form data:</strong> <code>file</code> (file), <code>node_id</code> (string)
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/download/{file_id}</span><br>
                Download a file from cloud storage<br>
                <strong>Query params:</strong> <code>node_id</code> (required) - requesting node ID
            </div>
            
            <h2>📖 Usage Examples</h2>
            <p><strong>Upload file:</strong> <code>curl -X POST -F "file=@example.txt" -F "node_id=CloudNode1" http://localhost:8081/api/upload</code></p>
            <p><strong>List files:</strong> <code>curl http://localhost:8081/api/files?node_id=CloudNode1</code></p>
            <p><strong>Download file:</strong> <code>curl http://localhost:8081/api/download/FILE_ID?node_id=CloudNode1 -o downloaded_file.txt</code></p>
            
            <h2>🎛️ Interactive Dashboard</h2>
            <p><a href="/dashboard" style="display: inline-block; background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">🚀 Open Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, 
                                connected=api_client.is_connected(),
                                controller_host=CONTROLLER_HOST,
                                controller_port=CONTROLLER_PORT)

@app.route('/api/status')
def api_status():
    """Get API status and controller connection"""
    api_client.reconnect_if_needed()
    
    return jsonify({
        'api_version': '1.0.0',
        'controller_connected': api_client.is_connected(),
        'controller_host': CONTROLLER_HOST,
        'controller_port': CONTROLLER_PORT,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/nodes')
def list_nodes():
    """Get list of all registered nodes"""
    try:
        nodes = []
        node_storage_dir = 'node_storage'
        
        if os.path.exists(node_storage_dir):
            for node_dir in os.listdir(node_storage_dir):
                node_path = os.path.join(node_storage_dir, node_dir)
                config_file = os.path.join(node_path, 'node_config.json')
                
                if os.path.isdir(node_path) and os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        host = config.get('host', 'localhost')
                        port = config.get('port', 0)
                        
                        # Check real-time node status
                        is_online = check_node_online(host, port)
                        status = 'online' if is_online else 'offline'
                        
                        nodes.append({
                            'node_id': config.get('node_id', node_dir),
                            'host': host,
                            'port': port,
                            'status': status,
                            'last_heartbeat': config.get('last_heartbeat', ''),
                            'resources': {
                                'cpu_cores': config.get('cpu_cores', 0),
                                'cpu_speed': config.get('cpu_speed', 0),
                                'ram_gb': config.get('ram_gb', 0),
                                'storage_gb': config.get('storage_gb', 0),
                                'bandwidth_mbps': config.get('bandwidth_mbps', 0)
                            }
                        })
                    except json.JSONDecodeError:
                        continue
        
        return jsonify({
            'total_nodes': len(nodes),
            'online_nodes': len([n for n in nodes if n['status'] == 'online']),
            'nodes': nodes
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get nodes: {str(e)}'}), 500

@app.route('/api/files')
def list_files():
    """List files in cloud storage"""
    node_id = request.args.get('node_id', 'web_api')
    
    try:
        files = []
        metadata_dir = 'cloud_storage/metadata'
        
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    metadata_path = os.path.join(metadata_dir, metadata_file)
                    try:
                        with open(metadata_path, 'r') as f:
                            file_meta = json.load(f)
                        
                        files.append({
                            'file_id': file_meta.get('file_id', ''),
                            'filename': file_meta.get('filename', ''),
                            'size': file_meta.get('size', 0),
                            'checksum': file_meta.get('checksum', ''),
                            'chunk_count': file_meta.get('chunk_count', 0),
                            'upload_date': file_meta.get('upload_date', ''),
                            'uploading_node': file_meta.get('uploading_node', ''),
                            'replica_nodes': file_meta.get('replica_nodes', []),
                            'online_replicas': file_meta.get('online_replicas', 0)
                        })
                    except json.JSONDecodeError:
                        continue
        
        return jsonify({
            'total_files': len(files),
            'total_size': sum(f['size'] for f in files),
            'files': files,
            'requesting_node': node_id
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/api/files/<file_id>')
def get_file_info(file_id):
    """Get detailed information about a specific file"""
    api_client.reconnect_if_needed()
    
    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503
    
    try:
        response = api_client.stub.GetFileInfo(
            file_service_pb2.FileInfoRequest(file_id=file_id)
        )
        
        if not response.found:
            return jsonify({'error': 'File not found'}), 404
        
        file_info = response.file_info
        return jsonify({
            'file_id': file_info.file_id,
            'filename': file_info.filename,
            'size': file_info.size,
            'checksum': file_info.checksum,
            'chunk_count': file_info.chunk_count,
            'upload_date': file_info.upload_date,
            'uploading_node': file_info.uploading_node,
            'replica_nodes': list(file_info.replica_nodes),
            'online_replicas': file_info.online_replicas
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to cloud storage"""
    api_client.reconnect_if_needed()
    
    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    node_id = request.form.get('node_id', 'web_api')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE} bytes'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        # Read file and create chunks
        def generate_upload_requests():
            # First request with metadata
            yield file_service_pb2.UploadRequest(
                metadata=file_service_pb2.FileMetadata(
                    filename=filename,
                    uploading_node=node_id
                )
            )
            
            # Subsequent requests with file chunks
            chunk_size = 64 * 1024  # 64KB chunks
            with open(temp_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield file_service_pb2.UploadRequest(chunk=chunk)
        
        # Upload file via gRPC
        response = api_client.stub.UploadFile(generate_upload_requests())
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': response.success,
            'message': response.message,
            'file_id': response.file_id if response.success else None,
            'filename': filename,
            'uploading_node': node_id
        })
    
    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/nodes', methods=['POST'])
def create_node():
    """Create a new Z-Cloud node"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['node_id', 'host', 'port', 'cpu_cores', 'cpu_speed', 'ram_gb', 'storage_gb', 'bandwidth_mbps']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if node already exists
        node_storage_path = f'node_storage/{data["node_id"]}'
        if os.path.exists(node_storage_path):
            return jsonify({'error': f'Node {data["node_id"]} already exists'}), 409
        
        # Create node storage directory
        os.makedirs(node_storage_path, exist_ok=True)
        os.makedirs(f'{node_storage_path}/local_files', exist_ok=True)
        os.makedirs(f'{node_storage_path}/replicas', exist_ok=True)
        os.makedirs(f'{node_storage_path}/temp', exist_ok=True)
        
        # Generate MAC address if not provided
        mac_address = data.get('mac_address')
        if not mac_address:
            import hashlib
            mac_hash = hashlib.md5(data['node_id'].encode()).hexdigest()[:12]
            mac_address = ':'.join([mac_hash[i:i+2] for i in range(0, 12, 2)])
        
        # Create node configuration file
        node_config = {
            'node_id': data['node_id'],
            'host': data['host'],
            'port': int(data['port']),
            'cpu_cores': int(data['cpu_cores']),
            'cpu_speed': float(data['cpu_speed']),
            'ram_gb': int(data['ram_gb']),
            'storage_gb': int(data['storage_gb']),
            'bandwidth_mbps': int(data['bandwidth_mbps']),
            'mac_address': mac_address,
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }
        
        # Save node configuration
        config_path = f'{node_storage_path}/node_config.json'
        with open(config_path, 'w') as f:
            json.dump(node_config, f, indent=2)
        
        # Automatically start the node in a new terminal after creation
        node_command = f'python node.py --node-id {data["node_id"]} --host {data["host"]} --port {data["port"]} --cpu {data["cpu_cores"]} --cpu-speed {data["cpu_speed"]} --ram {data["ram_gb"]} --storage {data["storage_gb"]} --bandwidth {data["bandwidth_mbps"]}'
        
        import subprocess
        try:
            # Use PowerShell to start a new terminal with the node command
            powershell_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd {os.getcwd()}; {node_command}"'
            subprocess.run(['powershell', '-Command', powershell_command], check=True)
            
            # Update status to starting since we launched it
            node_config['status'] = 'starting'
            node_config['start_requested_at'] = datetime.now().isoformat()
            
            with open(config_path, 'w') as f:
                json.dump(node_config, f, indent=2)
            
            return jsonify({
                'success': True,
                'message': f'Node {data["node_id"]} created and started in new terminal',
                'node_config': node_config,
                'storage_path': node_storage_path,
                'command': node_command,
                'auto_started': True
            }), 201
        except subprocess.CalledProcessError as e:
            # If terminal launch fails, still return success for node creation
            return jsonify({
                'success': True,
                'message': f'Node {data["node_id"]} created successfully, but failed to auto-start: {str(e)}',
                'node_config': node_config,
                'storage_path': node_storage_path,
                'auto_started': False
            }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create node: {str(e)}'}), 500

@app.route('/api/nodes/<node_id>/start', methods=['POST'])
def start_node(node_id):
    """Start a Z-Cloud node in a new terminal"""
    try:
        node_storage_path = f'node_storage/{node_id}'
        config_path = f'{node_storage_path}/node_config.json'
        
        if not os.path.exists(config_path):
            return jsonify({'error': f'Node {node_id} not found'}), 404
        
        # Load node configuration
        with open(config_path, 'r') as f:
            node_config = json.load(f)
        
        # Update status to starting
        node_config['status'] = 'starting'
        node_config['start_requested_at'] = datetime.now().isoformat()
        
        # Save updated configuration
        with open(config_path, 'w') as f:
            json.dump(node_config, f, indent=2)
        
        # Construct the command to start the node
        node_command = f'python node.py --node-id {node_id} --host {node_config["host"]} --port {node_config["port"]} --cpu {node_config["cpu_cores"]} --cpu-speed {node_config["cpu_speed"]} --ram {node_config["ram_gb"]} --storage {node_config["storage_gb"]} --bandwidth {node_config["bandwidth_mbps"]}'
        
        # Start the node in a new PowerShell terminal
        import subprocess
        try:
            # Use PowerShell to start a new terminal with the node command
            powershell_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd {os.getcwd()}; {node_command}"'
            subprocess.run(['powershell', '-Command', powershell_command], check=True)
            
            return jsonify({
                'success': True,
                'message': f'Node {node_id} started in new terminal',
                'node_config': node_config,
                'command': node_command
            })
        except subprocess.CalledProcessError as e:
            return jsonify({
                'success': False,
                'error': f'Failed to start terminal: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to start node: {str(e)}'}), 500

@app.route('/api/download/<file_id>')
def download_file(file_id):
    """Download a file from cloud storage"""
    api_client.reconnect_if_needed()

    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503

    node_id = request.args.get('node_id')
    if not node_id:
        return jsonify({'error': 'node_id parameter required'}), 400

    try:
        # Request file download
        response = api_client.stub.DownloadFile(
            file_service_pb2.DownloadRequest(
                file_id=file_id,
                requesting_node=node_id
            )
        )

        if not response.success:
            return jsonify({'error': response.message}), 404

        # Create temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_path = temp_file.name

        # Write file chunks to temporary file
        for chunk_response in response:
            if chunk_response.chunk:
                temp_file.write(chunk_response.chunk)

        temp_file.close()

        # Get original filename from file info
        file_info_response = api_client.stub.GetFileInfo(
            file_service_pb2.FileInfoRequest(file_id=file_id)
        )

        filename = file_info_response.file_info.filename if file_info_response.found else f"file_{file_id}"

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# ===== USER MANAGEMENT ENDPOINTS =====

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user and send OTP for email verification"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400

        email = data['email'].strip().lower()
        password = data['password']

        # Basic validation
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email address is required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        # Register user
        result = user_manager.register_user(email, password)

        if not result['success']:
            return jsonify({'error': result['message']}), 400

        # Generate and send OTP for email verification
        try:
            otp = generate_otp()
            expiry = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
            
            OTP_STORAGE[email] = {
                'code': otp,
                'expiry': expiry,
                'attempts': 0,
                'is_registration': True  # Mark as registration OTP
            }
            
            # Send OTP email (prints to console in dev)
            send_otp_email(email, otp)
            
            print(f"OTP generated for {email}: {otp}")
            
            return jsonify({
                'success': True,
                'message': 'Account created. Please verify your email with the OTP sent to your inbox.',
                'email': email,
                'requires_otp': True
            }), 201
        except Exception as otp_error:
            print(f"OTP generation error: {str(otp_error)}")
            return jsonify({
                'success': True,
                'message': f'Account created, but OTP generation failed: {str(otp_error)}. Please try again.',
                'email': email,
                'requires_otp': False,
                'error': str(otp_error)
            }), 201

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_email():
    """Verify user email with verification code"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'code' not in data:
            return jsonify({'error': 'Email and verification code are required'}), 400

        email = data['email'].strip().lower()
        code = data['code'].strip()

        result = user_manager.verify_email(email, code)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/auth/verify-registration-otp', methods=['POST'])
def verify_registration_otp():
    """Verify OTP for new user registration"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'otp' not in data:
            return jsonify({'error': 'Email and OTP are required'}), 400

        email = data['email'].strip().lower()
        otp = data['otp'].strip()

        # Check if OTP exists
        if email not in OTP_STORAGE:
            return jsonify({'error': 'OTP expired or not requested'}), 401

        otp_data = OTP_STORAGE[email]

        # Check if this is a registration OTP
        if not otp_data.get('is_registration', False):
            return jsonify({'error': 'Invalid OTP request type'}), 401

        # Check OTP expiry
        if datetime.now() > otp_data['expiry']:
            del OTP_STORAGE[email]
            return jsonify({'error': 'OTP expired. Please register again.'}), 401

        # Check attempts
        if otp_data['attempts'] >= MAX_OTP_ATTEMPTS:
            del OTP_STORAGE[email]
            return jsonify({'error': 'Too many failed attempts. Please register again.'}), 401

        # Verify OTP
        if otp != otp_data['code']:
            otp_data['attempts'] += 1
            return jsonify({'error': f'Invalid OTP. {MAX_OTP_ATTEMPTS - otp_data["attempts"]} attempts remaining.'}), 401

        # OTP verified - mark user as verified
        del OTP_STORAGE[email]
        
        # Mark email as verified in user_manager
        user_manager.verify_email(email, otp)

        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now log in.',
            'user': {'email': email}
        }), 200

    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP code to user email for authentication"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400

        email = data['email'].strip().lower()
        password = data['password']

        # Verify email and password first
        result = user_manager.authenticate_user(email, password)
        if not result['success']:
            return jsonify({'error': result['message']}), 401

        # Generate OTP
        otp = generate_otp()
        expiry = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

        # Store OTP
        OTP_STORAGE[email] = {
            'code': otp,
            'expiry': expiry,
            'attempts': 0,
            'password': password  # Store temporarily for verification
        }

        # Send OTP email
        if send_otp_email(email, otp):
            return jsonify({
                'success': True,
                'message': 'OTP sent to your email',
                'email': email
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500

    except Exception as e:
        # Handle encoding issues by providing a safe error message
        error_msg = str(e)
        # Replace any Unicode characters that might cause encoding issues
        safe_error = error_msg.encode('ascii', 'ignore').decode('ascii')
        if not safe_error:
            safe_error = "Unknown error occurred while sending OTP"
        return jsonify({'error': f'Failed to send OTP: {safe_error}'}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and authenticate user"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'otp' not in data:
            return jsonify({'error': 'Email and OTP are required'}), 400

        email = data['email'].strip().lower()
        otp = data['otp'].strip()

        # Check if OTP exists
        if email not in OTP_STORAGE:
            return jsonify({'error': 'OTP expired or not requested'}), 401

        otp_data = OTP_STORAGE[email]

        # Check OTP expiry
        if datetime.now() > otp_data['expiry']:
            del OTP_STORAGE[email]
            return jsonify({'error': 'OTP expired. Please request a new one.'}), 401

        # Check attempts
        if otp_data['attempts'] >= MAX_OTP_ATTEMPTS:
            del OTP_STORAGE[email]
            return jsonify({'error': 'Too many failed attempts. Please request a new OTP.'}), 401

        # Verify OTP
        if otp != otp_data['code']:
            otp_data['attempts'] += 1
            return jsonify({'error': f'Invalid OTP. {MAX_OTP_ATTEMPTS - otp_data["attempts"]} attempts remaining.'}), 401

        # OTP verified successfully
        del OTP_STORAGE[email]

        # Mark user as verified and update last login
        user_manager.verify_email(email, otp)
        
        # Store user session
        session['user_email'] = email
        session['authenticated'] = True

        return jsonify({
            'success': True,
            'message': 'Authentication successful',
            'user': {
                'email': email,
                'verified': True
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'OTP verification failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Authenticate user login"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400

        email = data['email'].strip().lower()
        password = data['password']

        result = user_manager.authenticate_user(email, password)

        if result['success']:
            # Store user session (simplified - in production use proper session management)
            session['user_email'] = email
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': result['user_data']
            }), 200
        else:
            return jsonify({'error': result['message']}), 401

    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    session.pop('user_email', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/api/auth/status')
def auth_status():
    """Get current authentication status"""
    user_email = session.get('user_email')
    if user_email:
        user_info = user_manager.get_user_info(user_email)
        if user_info:
            return jsonify({
                'authenticated': True,
                'user': {
                    'email': user_email,
                    'verified': user_info.get('verified', False),
                    'last_login': user_info.get('last_login')
                }
            }), 200

    return jsonify({'authenticated': False}), 200

@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification code"""
    try:
        data = request.get_json()

        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        email = data['email'].strip().lower()

        result = user_manager.resend_verification(email)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f'Failed to resend verification: {str(e)}'}), 500

# ===== STORAGE INFORMATION ENDPOINTS =====

@app.route('/api/storage/info')
def storage_info():
    """Get overall storage information"""
    try:
        # Get storage info from user manager (placeholder for now)
        storage_data = user_manager.get_storage_info()

        # Try to get real node data from controller
        nodes_data = []
        try:
            api_client.reconnect_if_needed()
            if api_client.is_connected():
                # Get nodes from controller
                nodes_response = api_client.stub.GetNodeStatus(
                    file_service_pb2.NodeStatusRequest(target_node_id="")
                )
                nodes_data = []
                for node in nodes_response.nodes:
                    nodes_data.append({
                        'node_id': node.node_id,
                        'online': node.is_online,
                        'storage_gb': node.resources.storage_bytes / (1024**3),
                        'cpu_cores': node.resources.cpu_cores,
                        'ram_gb': node.resources.ram_bytes / (1024**3)
                    })

                # Calculate real storage stats
                online_nodes = [n for n in nodes_data if n['online']]
                total_storage = sum(n['storage_gb'] for n in nodes_data)
                storage_data.update({
                    'total_storage_gb': total_storage,
                    'active_nodes': len(online_nodes),
                    'total_nodes': len(nodes_data),
                    'nodes': nodes_data
                })

        except Exception as e:
            # If controller not available, use placeholder data
            print(f"Controller not available for storage info: {e}")

        return jsonify(storage_data), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get storage info: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Z-Cloud Web API...")
    print(f"Controller: {CONTROLLER_HOST}:{CONTROLLER_PORT}")
    print(f"Web API: http://localhost:8081")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    
    app.run(host='0.0.0.0', port=8081, debug=True)