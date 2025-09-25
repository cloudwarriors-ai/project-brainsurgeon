import WebSocket from 'ws';

// Configuration
const SESSION_NAME = 'pts-32.nasty-speed';
const WS_URL = `ws://localhost:3001?session=${encodeURIComponent(SESSION_NAME)}`;

console.log(`Connecting to session: ${SESSION_NAME}`);
console.log(`WebSocket URL: ${WS_URL}`);

// Create WebSocket connection
const ws = new WebSocket(WS_URL);

ws.on('open', () => {
    console.log('✓ Connected to screen session');
    
    // Send some test commands
    setTimeout(() => {
        console.log('Sending commands...');
        
        // Clear screen and show session info
        ws.send(JSON.stringify({ type: 'input', data: 'clear\r' }));
        
        setTimeout(() => {
            ws.send(JSON.stringify({ type: 'input', data: 'echo "Connected to session via automation"\r' }));
        }, 500);
        
        setTimeout(() => {
            ws.send(JSON.stringify({ type: 'input', data: 'whoami\r' }));
        }, 1000);
        
        setTimeout(() => {
            ws.send(JSON.stringify({ type: 'input', data: 'pwd\r' }));
        }, 1500);
        
        setTimeout(() => {
            ws.send(JSON.stringify({ type: 'input', data: 'date\r' }));
        }, 2000);
        
        // Close connection after commands
        setTimeout(() => {
            console.log('Closing connection...');
            ws.close();
        }, 5000);
        
    }, 1000);
});

ws.on('message', (data) => {
    try {
        const message = JSON.parse(data);
        
        switch (message.type) {
            case 'output':
                process.stdout.write(message.data);
                break;
            case 'error':
                console.error(`\x1b[31mERROR: ${message.data}\x1b[0m`);
                break;
            case 'exit':
                console.log(`\nSession exited with code: ${message.code}`);
                break;
            case 'connected':
                console.log(`Connected to session: ${message.session}`);
                break;
        }
    } catch (error) {
        console.error('Error parsing message:', error);
        console.log('Raw data:', data.toString());
    }
});

ws.on('error', (error) => {
    console.error('WebSocket error:', error.message);
});

ws.on('close', () => {
    console.log('\n✓ Connection closed');
    process.exit(0);
});

// Handle process interruption
process.on('SIGINT', () => {
    console.log('\nInterrupted, closing connection...');
    ws.close();
});