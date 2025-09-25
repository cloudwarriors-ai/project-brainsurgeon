#!/bin/bash

# Check for custom domain
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <your-custom-domain>"
    echo "   Example: $0 terminal.yourdomain.com"
    exit 1
fi

CUSTOM_DOMAIN=$1
echo "🚀 Starting Screen Terminal Server with Ngrok"
echo "🌐 Using custom domain: $CUSTOM_DOMAIN"

# Kill existing processes
pkill -f "node screen-terminal-server.js" 2>/dev/null || true
pkill -f "ngrok.*3000" 2>/dev/null || true
pkill -f "ngrok.*3001" 2>/dev/null || true
sleep 2

# Start server
node screen-terminal-server.js &
sleep 3

# Start ngrok tunnels with custom domain
echo "🌐 Starting ngrok tunnel for HTTP server..."
ngrok http --domain=$CUSTOM_DOMAIN 3000 &
NGROK_HTTP_PID=$!

echo "🔌 Starting ngrok tunnel for WebSocket server..."
ngrok http 3001 &
NGROK_WS_PID=$!

sleep 5

# Get URLs
HTTP_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
WS_URL=$(curl -s http://localhost:4041/api/tunnels | jq -r '.tunnels[0].public_url')
WS_URL=$(echo "$WS_URL" | sed 's/https:/wss:/')

echo ""
echo "🎉 READY!"
echo "Web Interface: $HTTP_URL"
echo "WebSocket: $WS_URL"
echo ""
echo "Run ./stop.sh to stop all services"