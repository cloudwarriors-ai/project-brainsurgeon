# Custom Domain Setup for Screen Terminal Server

## Prerequisites

1. **ngrok Account**: Sign up at https://ngrok.com/
2. **Custom Domain**: Have a domain you want to use
3. **Domain Configuration**: Configure your domain with ngrok

## Step 1: Configure Custom Domain in ngrok

### Option A: Using ngrok Dashboard (Recommended)
1. Log in to your [ngrok dashboard](https://dashboard.ngrok.com/)
2. Go to **Domains** section
3. Click **"Add a domain"**
4. Enter your custom domain (e.g., `terminal.yourdomain.com`)
5. Follow the DNS configuration instructions provided by ngrok

### Option B: Using ngrok CLI
```bash
# Add your domain to ngrok
ngrok domains add terminal.yourdomain.com

# Follow the DNS instructions provided
```

## Step 2: Configure DNS

After adding your domain to ngrok, you'll need to configure DNS records:

1. **CNAME Record** (recommended):
   ```
   Type: CNAME
   Name: terminal
   Value: <your-ngrok-target-domain>
   TTL: 300 (or default)
   ```

2. **OR A Record** (if CNAME not available):
   ```
   Type: A
   Name: terminal
   Value: <ngrok-IP-address>
   TTL: 300
   ```

## Step 3: Configure the Project

### Edit Configuration File
```bash
# Edit the config file
nano config.sh
```

Set your custom domain:
```bash
# Your custom domain configured in ngrok
CUSTOM_DOMAIN="terminal.yourdomain.com"

# Optional: Add ngrok auth token for better reliability
NGROK_AUTH_TOKEN="your_ngrok_auth_token_here"
```

### Get ngrok Auth Token (Optional but Recommended)
1. Go to [ngrok dashboard](https://dashboard.ngrok.com/)
2. Navigate to **Your Authtoken**
3. Copy your authtoken
4. Paste it in `config.sh`

## Step 4: Launch the Service

### Simple Launch
```bash
# Using the custom domain launcher
./start-custom.sh
```

### Manual Launch
```bash
# Or use the basic launcher with domain parameter
./start.sh terminal.yourdomain.com
```

## Step 5: Verify Setup

After launching, you should see output like:
```
🎉 READY!
==============================================
🌐 Web Interface: https://terminal.yourdomain.com
🔌 WebSocket: wss://some-random-domain.ngrok.io
```

### Test the Setup
1. Open the web interface URL in your browser
2. You should see the screen terminal interface
3. Connect to a screen session
4. Verify that terminal resizing works

## Troubleshooting

### Domain Not Configured
If you see an error like:
```
ERR_NGROK_3200: the domain 'terminal.yourdomain.com' is not configured for this account
```

**Solution:**
1. Verify the domain is added to your ngrok account
2. Check DNS propagation (may take 24-48 hours)
3. Ensure you're using the correct domain name

### DNS Propagation Issues
```bash
# Check if DNS is properly configured
nslookup terminal.yourdomain.com

# Or use dig for more details
dig terminal.yourdomain.com
```

### SSL Certificate Issues
ngrok automatically handles SSL certificates for custom domains. If you see SSL errors:
1. Wait a few minutes for ngrok to provision certificates
2. Verify your domain is properly configured in ngrok dashboard
3. Check that DNS is correctly pointing to ngrok

### WebSocket Connection Issues
If the WebSocket doesn't connect:
1. Ensure both ngrok tunnels are running
2. Check that the frontend is using the correct WebSocket URL
3. Verify the screen session exists and is detached

## Advanced Configuration

### Multiple Domains
You can create multiple launch scripts for different domains:
```bash
# Create a script for each domain
cp start-custom.sh start-prod.sh
cp start-custom.sh start-dev.sh

# Edit each script with different domains
# Or use config files:
cp config.sh config-prod.sh
cp config.sh config-dev.sh
```

### Subdomain Routing
You can use different subdomains:
- `terminal.yourdomain.com` - main terminal interface
- `term.yourdomain.com` - short URL
- `console.yourdomain.com` - alternative interface

### Port Configuration
If you need to use different ports:
1. Edit `screen-terminal-server.js` to change ports
2. Update the launch scripts accordingly
3. Ensure ngrok tunnels point to the correct ports

## Security Considerations

### Domain Security
- Keep your ngrok auth token secure
- Use strong, random subdomains
- Regularly rotate your ngrok auth token

### Access Control
Consider adding authentication to your web interface:
```javascript
// Add to screen-terminal-server.js before app.listen()
app.use((req, res, next) => {
    const auth = req.headers.authorization;
    if (auth && auth === 'Bearer your-secret-token') {
        next();
    } else {
        res.status(401).send('Unauthorized');
    }
});
```

### Rate Limiting
Add rate limiting to prevent abuse:
```bash
# Install rate limiter
npm install express-rate-limit

# Add to your server
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);
```

## Production Deployment

For production use, consider:

1. **Process Management**: Use PM2 or systemd to keep the service running
2. **Monitoring**: Add health checks and monitoring
3. **Logging**: Implement proper log rotation
4. **Backup**: Regular backup of screen sessions if needed
5. **SSL**: Use ngrok's built-in SSL or your own certificates

### PM2 Setup
```bash
# Install PM2
npm install -g pm2

# Create ecosystem.config.js
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'screen-terminal',
    script: 'screen-terminal-server.js',
    instances: 1,
    exec_mode: 'fork',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

This setup provides a robust, custom-domain-based terminal interface accessible from anywhere!