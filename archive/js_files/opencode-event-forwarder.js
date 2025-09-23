/**
 * Opencode Bridge Event Forwarder
 * 
 * This script captures events from the opencode-bridge and forwards them
 * to a background agent API.
 */

import axios from 'axios';

// Configuration
const AGENT_ENDPOINT = process.env.AGENT_ENDPOINT || 'http://localhost:3000/agent';
const EVENT_BUFFER_SIZE = 10; // Number of events to buffer before sending as batch
const RETRY_DELAY_MS = 1000;  // Delay between retries on error

// Event buffer
const eventBuffer = [];

/**
 * Forwards events to the background agent
 * @param {Object|Array} events - Single event or array of events to forward
 */
async function forwardToAgent(events) {
  try {
    const payload = Array.isArray(events) ? { events } : { event: events };
    
    await axios.post(AGENT_ENDPOINT, payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const eventCount = Array.isArray(events) ? events.length : 1;
    console.log(`Successfully forwarded ${eventCount} event(s) to agent`);
    return true;
  } catch (error) {
    console.error('Failed to forward event(s) to agent:', error.message);
    return false;
  }
}

/**
 * Adds an event to the buffer and flushes if buffer is full
 * @param {Object} event - The event to add to the buffer
 */
async function bufferEvent(event) {
  eventBuffer.push(event);
  
  if (eventBuffer.length >= EVENT_BUFFER_SIZE) {
    await flushEventBuffer();
  }
}

/**
 * Flushes the event buffer, sending all events to the agent
 */
async function flushEventBuffer() {
  if (eventBuffer.length === 0) return;
  
  const events = [...eventBuffer];
  eventBuffer.length = 0; // Clear the buffer
  
  const success = await forwardToAgent(events);
  
  if (!success) {
    // On failure, add events back to the beginning of the buffer
    eventBuffer.unshift(...events);
    console.log(`Added ${events.length} events back to buffer after failed forwarding attempt`);
  }
}

/**
 * Sets up interval to periodically flush event buffer even if not full
 */
function setupPeriodicFlush() {
  // Flush buffer every 5 seconds even if not full
  setInterval(flushEventBuffer, 5000);
}

/**
 * Main event processing loop that uses the opencode-bridge API
 */
async function processOpencodeEvents() {
  // Set up periodic buffer flushing
  setupPeriodicFlush();
  
  while (true) {
    try {
      // Get next event using the opencode-bridge API
      // Note: In a real implementation, you would need to access this API
      // through the appropriate channels provided by opencode
      const event = await getNextOpencodeEvent();
      
      // Add the event to our buffer
      await bufferEvent(event);
      
    } catch (error) {
      console.error('Error processing event:', error.message);
      // Add a small delay before retrying
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
    }
  }
}

/**
 * Gets the next event from the opencode-bridge API
 * This would need to be implemented based on how opencode exposes its API
 */
async function getNextOpencodeEvent() {
  // This is where you would call the actual opencode-bridge_get_next_event API
  // For now, this is a placeholder implementation
  
  return new Promise((resolve) => {
    // In reality, this would be replaced with the actual API call
    setTimeout(() => {
      resolve({
        type: 'simulated.event',
        properties: {
          timestamp: Date.now(),
          data: {
            message: 'This is a simulated event'
          }
        }
      });
    }, 2000);
  });
}

/**
 * Handles process termination and ensures event buffer is flushed
 */
function setupCleanShutdown() {
  const shutdown = async (signal) => {
    console.log(`Received ${signal}, flushing event buffer before exiting...`);
    await flushEventBuffer();
    console.log('Shutdown complete');
    process.exit(0);
  };
  
  // Handle termination signals
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));
}

// Main function
async function main() {
  console.log('Starting Opencode Bridge Event Forwarder...');
  setupCleanShutdown();
  await processOpencodeEvents();
}

// Start the forwarder
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});