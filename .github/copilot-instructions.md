<!-- .github/copilot-instructions.md for Z-Cloud (MbolePay1) -->
# Quick context

This repository implements Z-Cloud: a local, gRPC-backed distributed file system with a Flask Web API and an interactive network controller. The two primary runtime components are:
- `network_controller.py` — gRPC controller, node registry, replication, and an interactive terminal UI (default gRPC port 5000).
- `web_api.py` — Flask web server (dashboard + REST endpoints) that talks to the controller via `file_service_pb2[_grpc]` (default web port 8081 in `start_web_api.py`).

# What to know before editing

- Entry points: run `python start_web_api.py` to install deps and launch both services; alternately run `python network_controller.py` and `python web_api.py` separately.
- Controller ↔ Web API communication is via gRPC defined in `file_service.proto` and compiled artifacts `file_service_pb2.py` / `file_service_pb2_grpc.py` — regenerate these when changing the proto.
- Persistent state is file-based: `users.json`, `cloud_storage/metadata/*.json`, and `node_storage/*/node_config.json` are the canonical sources of truth.

# Typical developer workflows

- Start full dev stack (recommended):
```powershell
$env:EMAIL_PASSWORD="<optional_gmail_app_password>"
python start_web_api.py
```
- Manual startup (useful when iterating on one component):
```powershell
python network_controller.py    # controller on localhost:5000
python web_api.py               # web API on 8081 (see file for override)
```
- Run tests: the repo includes `test_otp_email.py` and `test_user_manager.py` — run with `pytest` (ensure `requirements.txt` installed).

# Important files & patterns (quick map)

- `web_api.py`: Flask routes, config constants to change (`CONTROLLER_HOST`, `CONTROLLER_PORT`, `UPLOAD_FOLDER`, `MAX_FILE_SIZE`, `SECRET_KEY`). OTP/email behavior prints OTP to console when `EMAIL_PASSWORD` is not set — useful for local dev.
- `network_controller.py`: gRPC server implementation and interactive command loop (`status`, `nodes`, `files`, `stats`, `help`). Storage root: `cloud_storage/` (metadata + temp_chunks).
- `start_web_api.py`: convenience launcher that checks files, installs `requirements.txt`, and spawns both processes while monitoring them.
- `user_manager.py`: `users.json`-backed user store, verification code lifecycle, and SMTP helper. Tests exercise this module.
- `file_service.proto` / `file_service_pb2*.py`: gRPC interface — update pb2 files after proto changes using `protoc`.
- `node.py`, `storage_virtual_node.py`, `cloud.py`: node runtime and cloud simulation used by `main.py` and for local testing.

# Integration & debugging tips

- To confirm connectivity: call `GET /api/status` on the web API (default http://localhost:8081/api/status) — it reports controller connectivity.
- When debugging email/OTP locally, note `web_api.py` will print OTP codes to console if `EMAIL_PASSWORD` is empty — no SMTP required for dev.
- Check `logs/`, `flask_session/`, and `cloud_storage/metadata/` for runtime artifacts and helpful diagnostics.
- If you change the gRPC surface, update `file_service_pb2.py` and `file_service_pb2_grpc.py` by re-running `protoc --python_out=. --grpc_python_out=. file_service.proto` (ensure gRPC tools installed).

# PR checklist for changes that affect runtime behavior

- Update `README.md` or the WEB_API_README.md when changing user-facing endpoints.
- Run unit tests (`pytest`) and smoke-test the stack with `start_web_api.py`.
- If proto changes: regenerate pb2 files and include them in the PR.
- Avoid committing secrets: change `app.config['SECRET_KEY']` and unset `EMAIL_PASSWORD` in shared branches.

# If this file already exists

If a `.github/copilot-instructions.md` already exists, preserve any repo-specific notes in it — merge important operational steps from this file into the existing one rather than overwriting blindly.

If anything here is unclear or you want examples added (e.g., sample `protoc` command for Windows, or command-line flags used by `network_controller.py`), tell me what to expand and I will update the file.
