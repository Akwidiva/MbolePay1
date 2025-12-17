# 🌐 Z-Cloud Web API

A modern web interface for the Z-Cloud distributed file system, providing REST API endpoints and an interactive dashboard for managing files and nodes.

## 🚀 Quick Start

### Option 1: Easy Startup (Recommended)
```bash
python start_web_api.py
```
This will automatically start both the network controller and web API server.

### Option 2: Manual Startup
1. **Start Network Controller:**
   ```bash
   python network_controller.py
   ```

2. **Start Web API Server:**
   ```bash
   python web_api.py
   ```

3. **Access the Dashboard:**
    Open http://localhost:8081/dashboard in your browser

## 📋 Features

### 🎛️ Interactive Dashboard
- **Real-time Node Monitoring**: View all connected nodes and their status
- **File Management**: Upload, download, and list files with a modern UI
- **Visual File Browser**: See file details, replicas, and metadata
- **Responsive Design**: Works on desktop and mobile devices

### 🔌 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | API and controller connection status |
| `GET` | `/api/nodes` | List all registered nodes |
| `GET` | `/api/files` | List files (with optional node filtering) |
| `GET` | `/api/files/{file_id}` | Get detailed file information |
| `POST` | `/api/upload` | Upload a file to cloud storage |
| `GET` | `/api/download/{file_id}` | Download a file from cloud storage |

## 📖 API Usage Examples

### Upload a File
```bash
curl -X POST \
  -F "file=@example.txt" \
  -F "node_id=CloudNode1" \
  http://localhost:8081/api/upload
```

### List Files
```bash
# List all files visible to a node
curl "http://localhost:8081/api/files?node_id=CloudNode1"

# List all files (as web_api)
curl "http://localhost:8081/api/files"
```

### Download a File
```bash
curl "http://localhost:8081/api/download/FILE_ID?node_id=CloudNode1" -o downloaded_file.txt
```

### Get Node Status
```bash
curl "http://localhost:8080/api/nodes"
```

### Check API Status
```bash
curl "http://localhost:8080/api/status"
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Web API       │    │ Network         │
│                 │◄──►│   (Flask)       │◄──►│ Controller      │
│   Dashboard     │    │   Port 8080     │    │ (gRPC)          │
└─────────────────┘    └─────────────────┘    │ Port 5000       │
                                              └─────────────────┘
                                                       ▲
                                                       │
                                              ┌─────────────────┐
                                              │   Z-Cloud Nodes      │
                                              │   (gRPC)        │
                                              └─────────────────┘
```

## 🔧 Configuration

### Web API Settings
Edit `web_api.py` to modify:
- **Controller Host/Port**: `CONTROLLER_HOST` and `CONTROLLER_PORT`
- **Upload Directory**: `UPLOAD_FOLDER`
- **Max File Size**: `MAX_FILE_SIZE`
- **Web Server Port**: Change in `app.run()` call

### Network Controller
The web API connects to the existing network controller on `localhost:5000` by default.

## 📁 File Structure

```
Z-Cloud/
├── web_api.py              # Flask web server
├── start_web_api.py        # Easy startup script
├── static/
│   └── index.html          # Interactive dashboard
├── web_uploads/            # Temporary upload directory
├── requirements.txt        # Updated with web dependencies
└── WEB_API_README.md       # This file
```

## 🔒 Security Features

- **File Visibility**: Respects the existing node visibility system
- **Secure Filenames**: Uses `secure_filename()` for uploads
- **File Size Limits**: Configurable maximum upload size
- **CORS Enabled**: Allows cross-origin requests for development
- **Input Validation**: Validates all API inputs

## 🌟 Dashboard Features

### Real-time Updates
- Auto-refreshes node status every 30 seconds
- Live connection status indicators
- Real-time file count and storage statistics

### File Operations
- **Drag & Drop Upload**: Modern file upload interface
- **One-click Download**: Direct download from file list
- **Node Filtering**: View files visible to specific nodes
- **File Details**: Complete metadata display

### Node Management
- **Status Monitoring**: CPU, memory, storage, bandwidth usage
- **Online/Offline Status**: Visual indicators for node health
- **Heartbeat Tracking**: Last seen timestamps

## 🐛 Troubleshooting

### Common Issues

**"Controller not available" error:**
- Ensure network controller is running on port 5000
- Check firewall settings
- Verify gRPC dependencies are installed

**Dashboard not loading:**
- Ensure `static/index.html` exists
- Check web server is running on port 8080
- Try accessing http://localhost:8080 directly

**Upload failures:**
- Check file size limits
- Ensure upload directory exists and is writable
- Verify node ID is valid and online

**Download issues:**
- Ensure requesting node has visibility to the file
- Check file exists and has available replicas
- Verify node ID parameter is provided

### Debug Mode
To enable Flask debug mode, modify `web_api.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## 🔄 Integration with Existing System

The web API seamlessly integrates with the existing Z-Cloud system:

- **Respects File Visibility**: Only shows files to nodes that were online during upload
- **Uses Existing Replication**: Files uploaded via web API are replicated using the same logic
- **Node Management**: Works with existing node registration and heartbeat system
- **Storage Compatibility**: Uses the same cloud storage structure

## 📊 Monitoring

The web API provides comprehensive monitoring:

- **API Status**: Connection health to network controller
- **Node Statistics**: Real-time resource usage
- **File Metrics**: Storage usage and replication status
- **System Health**: Auto-restart capabilities with `start_web_api.py`

## 🚀 Production Deployment

For production use:

1. **Use a Production WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 web_api:app
   ```

2. **Configure Reverse Proxy** (nginx example):
   ```nginx
   location / {
       proxy_pass http://localhost:8080;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

3. **Environment Variables**:
   ```bash
   export CONTROLLER_HOST=your-controller-host
   export CONTROLLER_PORT=5000
   export FLASK_ENV=production
   ```

## 📝 License

This web API extension follows the same license as the main Z-Cloud project.

---

**Happy file sharing! 🎉**

For more information about the core Z-Cloud system, see the main README.md file.
