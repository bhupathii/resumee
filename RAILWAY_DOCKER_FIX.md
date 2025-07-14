# 🔧 Railway Docker Container Startup Fix

## 🚨 Error: `The executable 'cd' could not be found`

This error occurs when Railway tries to execute `cd` as a standalone command in a Docker container, but `cd` is a shell built-in, not an executable.

## ✅ Fix Applied

### Root Cause
The issue was in the `railway.toml` configuration:
```toml
[deploy]
startCommand = "cd tailorcv-backend && python app.py"  # ❌ Fails
```

The Docker container was trying to execute `cd` directly, which doesn't work because:
- `cd` is a shell built-in command, not an executable
- Docker containers need explicit shell commands for complex operations

### Solution
Updated the configuration to use the correct path directly:
```toml
[deploy]
startCommand = "python tailorcv-backend/app.py"  # ✅ Works
```

## 🔧 Configuration Changes

### 1. Updated `railway.toml`
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python tailorcv-backend/app.py"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### 2. Updated `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python39", "nodejs-18_x", "postgresql"]

[phases.install]
cmds = [
    "pip install -r requirements.txt"
]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "python tailorcv-backend/app.py"
```

## 🚀 How This Works

### Monorepo Structure
```
/
├── tailorcv-backend/
│   ├── app.py          # Flask application
│   ├── services/
│   └── ...
├── requirements.txt    # Python dependencies (root level)
└── railway.toml       # Railway configuration
```

### Deployment Flow
1. **Railway clones repository** to `/app`
2. **Installs dependencies** from root `requirements.txt`
3. **Starts application** with `python tailorcv-backend/app.py`
4. **Python finds the app** at the correct path
5. **Flask starts** and serves on the configured port

## 📋 Alternative Solutions

If the current fix doesn't work, here are other approaches:

### Option 1: Use Shell Command
```toml
[deploy]
startCommand = "sh -c 'cd tailorcv-backend && python app.py'"
```

### Option 2: Use Dockerfile WORKDIR
The Dockerfile already sets the working directory correctly:
```dockerfile
WORKDIR /app/tailorcv-backend
CMD ["python", "app.py"]
```

### Option 3: Move Files to Root
Move all backend files to the root directory (not recommended for monorepo).

## ✅ Expected Results

After this fix:
- ✅ Railway builds the Docker container successfully
- ✅ Container starts without `cd` executable error
- ✅ Python finds and runs the Flask application
- ✅ Health check passes at `/api/health`
- ✅ Backend is accessible from frontend

## 🔍 Monitoring

Check Railway deployment logs for:
1. **Build success**: Docker image created
2. **Container start**: No `cd` executable error
3. **Application start**: Flask server running on port 5000
4. **Health check**: `/api/health` responding with 200

The container startup should now work correctly! 🚀