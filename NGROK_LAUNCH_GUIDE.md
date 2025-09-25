# Screen Terminal Server with Ngrok

## Quick Start

### 🚀 Launch with Ngrok (Recommended)

```bash
# Simple start
./start.sh

# Or use the comprehensive launcher (with monitoring)
./launch-with-ngrok.sh
```

### 🛑 Stop Services

```bash
./stop.sh
```

## What This Does

The launch scripts automatically:
1. **Start the screen terminal server** on ports 3000 (HTTP) and 3001 (WebSocket)
2. **Create ngrok tunnels** for external access
3. **Display the external URLs** you can use from anywhere
4. **Handle terminal resizing** automatically

## External Access URLs

After running `./start.sh`, you'll get URLs like:
- **Web Interface**: `https://f01d0ae2c687.ngrok.app`
- **WebSocket**: `wss://46209f21b4c0.ngrok.app`

## Features

✅ **Full Terminal Access**: Connect to any screen session
✅ **Dynamic Resizing**: Terminal automatically fits browser window
✅ **Real-time Communication**: Instant command execution and output
✅ **External Access**: Use from anywhere with internet
✅ **Session Management**: List, create, and connect to screen sessions

## Usage

1. **Launch the service**:
   ```bash
   ./start.sh
   ```

2. **Open the web interface**:
   - Copy the Web Interface URL from the output
   - Open it in your browser

3. **Connect to a session**:
   - View available screen sessions
   - Click on any session to connect
   - Terminal will automatically resize to fit your browser

4. **Use the terminal**:
   - Type commands as you would in a normal terminal
   - Terminal output appears in real-time
   - Resize your browser window - terminal will adjust automatically

## Advanced Options

### Comprehensive Launcher
For monitoring and detailed status:
```bash
./launch-with-ngrok.sh
```
This provides:
- Real-time service monitoring
- Process information
- Automatic URL detection
- Status updates

### Manual Launch
If you prefer to run components separately:
```bash
# Start server
node screen-terminal-server.js

# In another terminal, start ngrok tunnels
ngrok http 3000 &
ngrok http 3001 &
```

## Requirements

- Node.js (installed)
- ngrok (installed)
- Screen (Linux system utility)

## Troubleshooting

### Port Already in Use
```bash
# Stop any existing services
./stop.sh
# Wait a moment, then try again
./start.sh
```

### Ngrok Not Installed
```bash
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin
```

### WebSocket Connection Issues
- Ensure both ngrok tunnels are running
- Check that the WebSocket URL uses `wss://` (not `https://`)
- Verify the screen session exists and is detached

## Architecture

```
Browser → Ngrok (HTTPS) → Node.js Server → Screen Session
         ↓
Browser → Ngrok (WSS) → WebSocket Server → Terminal I/O
```

The setup uses two separate ngrok tunnels:
- **HTTP tunnel** (port 3000): Web interface and API
- **WebSocket tunnel** (port 3001): Real-time terminal communication

## Security Notes

- Ngrok provides HTTPS encryption
- Access is available to anyone with the URLs
- Consider adding authentication for production use
- Screen sessions run with the permissions of the user running the server