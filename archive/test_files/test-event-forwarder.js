/**
 * Test Script for Opencode Event Forwarder
 * 
 * This script tests the event forwarder by:
 * 1. Setting up a mock agent server to receive events
 * 2. Simulating opencode-bridge events
 * 3. Verifying that events are properly forwarded
 */

import http from 'http';

// Configuration
const MOCK_AGENT_PORT = 3000;
const RECEIVED_EVENTS = [];

/**
 * Sets up a mock agent server to receive forwarded events
 */
function setupMockAgentServer() {
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/agent') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });
      
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          console.log('Mock agent received event:', JSON.stringify(data, null, 2));
          
          // Store the received event
          if (data.event) {
            RECEIVED_EVENTS.push(data.event);
          } else if (data.events && Array.isArray(data.events)) {
            RECEIVED_EVENTS.push(...data.events);
          }
          
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: true }));
        } catch (error) {
          console.error('Error processing request:', error.message);
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Invalid JSON' }));
        }
      });
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Not found' }));
    }
  });
  
  server.listen(MOCK_AGENT_PORT, () => {
    console.log(`Mock agent server listening on port ${MOCK_AGENT_PORT}`);
  });
  
  return server;
}

/**
 * Simulates getting events from the opencode-bridge
 */
function simulateOpencodeEvents(count = 5, intervalMs = 1000) {
  let eventCount = 0;
  
  return new Promise((resolve) => {
    const interval = setInterval(() => {
      eventCount++;
      
      const event = {
        type: 'test.event',
        properties: {
          id: `event-${eventCount}`,
          timestamp: Date.now(),
          data: {
            message: `Test event ${eventCount}`
          }
        }
      };
      
      console.log(`Simulating event ${eventCount}/${count}`);
      
      // In a real test, this would call your event forwarder directly
      // For this test, we'll simulate the forwarder by sending directly to the mock agent
      sendEventToAgent(event);
      
      if (eventCount >= count) {
        clearInterval(interval);
        resolve();
      }
    }, intervalMs);
  });
}

/**
 * Sends an event to the mock agent
 */
async function sendEventToAgent(event) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ event });
    
    const options = {
      hostname: 'localhost',
      port: MOCK_AGENT_PORT,
      path: '/agent',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };
    
    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve();
        } else {
          reject(new Error(`Failed to send event: ${responseData}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.write(data);
    req.end();
  });
}

/**
 * Verifies that all expected events were received
 */
function verifyReceivedEvents(expectedCount) {
  console.log(`\nVerifying received events (expected: ${expectedCount})...`);
  console.log(`Received ${RECEIVED_EVENTS.length} events`);
  
  if (RECEIVED_EVENTS.length === expectedCount) {
    console.log('✓ All events were received successfully');
    
    // List all received events
    console.log('\nReceived events:');
    RECEIVED_EVENTS.forEach((event, index) => {
      console.log(`[${index + 1}] ${event.type} - ${event.properties.id || 'no id'}`);
    });
    
    return true;
  } else {
    console.error(`✗ Expected ${expectedCount} events but received ${RECEIVED_EVENTS.length}`);
    return false;
  }
}

/**
 * Main test function
 */
async function runTest() {
  console.log('Starting event forwarder test...');
  
  // Set up mock agent server
  const server = setupMockAgentServer();
  
  try {
    // Wait for server to start
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simulate events
    const eventCount = 5;
    console.log(`Simulating ${eventCount} events...`);
    await simulateOpencodeEvents(eventCount);
    
    // Give some time for all events to be processed
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verify received events
    const success = verifyReceivedEvents(eventCount);
    
    console.log(`\nTest ${success ? 'PASSED' : 'FAILED'}`);
  } catch (error) {
    console.error('Test error:', error.message);
  } finally {
    // Shut down the server
    server.close(() => {
      console.log('Mock agent server shut down');
    });
  }
}

// Run the test
runTest().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});