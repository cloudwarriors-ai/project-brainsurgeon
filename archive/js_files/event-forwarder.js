/**
 * Event Forwarder for Opencode Bridge
 * 
 * This script captures opencode-bridge events and forwards them to a background agent.
 */

// Configuration
const AGENT_ENDPOINT = process.env.AGENT_ENDPOINT || 'http://localhost:3000/agent';

// Import required modules
import axios from 'axios';

/**
 * Forwards events to the background agent
 * @param {Object} event - The event to forward
 */
async function forwardToAgent(event) {
  try {
    await axios.post(AGENT_ENDPOINT, {
      event: event
    });
    console.log(`Event of type "${event.type}" successfully forwarded to agent`);
  } catch (error) {
    console.error('Failed to forward event to agent:', error.message);
  }
}

/**
 * Main event processing loop
 */
async function processEvents() {
  // Placeholder for the opencode-bridge API access
  // In a real implementation, this would use the actual API to get events
  
  while (true) {
    try {
      // Get the next event from the opencode-bridge
      // This is a placeholder - in reality, you would use the appropriate API method
      const event = await getNextEvent();
      
      // Forward the event to the agent
      await forwardToAgent(event);
      
    } catch (error) {
      console.error('Error processing event:', error.message);
      // Add a small delay before retrying
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

/**
 * Simulates getting the next event
 * This is a placeholder for the actual API call
 */
async function getNextEvent() {
  // In a real implementation, this would use the opencode-bridge_get_next_event API
  return new Promise((resolve) => {
    // Simulating an event
    setTimeout(() => {
      resolve({
        type: 'simulated.event',
        properties: {
          timestamp: Date.now()
        }
      });
    }, 2000);
  });
}

// Start processing events
console.log('Starting event forwarder...');
processEvents().catch(error => {
  console.error('Fatal error in event processing:', error);
  process.exit(1);
});