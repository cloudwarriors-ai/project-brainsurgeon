import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createOpencodeClient } from "@opencode-ai/sdk";
import { EventSource } from "eventsource";

const client = createOpencodeClient({
  baseUrl: process.env.OPENCODE_BASE_URL || "http://localhost:6969",
  responseStyle: "data"
});

const eventQueue = [];

const eventSource = new EventSource("http://localhost:6969/event?directory=/root/code/project-brainsurgeon");

eventSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    eventQueue.push(data);
  } catch (e) {
    // ignore
  }
};

eventSource.onerror = (error) => {
  console.error("Event source error:", error);
};

const server = new Server(
  {
    name: "opencode-tui-controller",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {
        listChanged: false
      },
      methods: {
        "tools/list": {
          request: {
            type: "object",
            properties: {
              method: { type: "string", enum: ["tools/list"] },
              params: { type: "object" },
              id: { type: "string" }
            },
            required: ["method"]
          }
        },
        "tools/call": {
          request: {
            type: "object",
            properties: {
              method: { type: "string", enum: ["tools/call"] },
              params: { type: "object", properties: { name: { type: "string" }, arguments: { type: "object" } }, required: ["name"] },
              id: { type: "string" }
            },
            required: ["method", "params"]
          }
        }
      }
    },
  }
);

// server.setRequestHandler("tools/list", {}, async () => {
//   return {
//     tools: [
//       {
//         name: "append_prompt",
//         description: "Append text to the TUI prompt",
//         inputSchema: {
//           type: "object",
//           properties: {
//             text: {
//               type: "string",
//               description: "The text to append to the prompt",
//             },
//           },
//           required: ["text"],
//         },
//       },
//       {
//         name: "submit_prompt",
//         description: "Submit the current prompt in the TUI",
//         inputSchema: {
//           type: "object",
//           properties: {},
//         },
//       },
//       {
//         name: "clear_prompt",
//         description: "Clear the current prompt in the TUI",
//         inputSchema: {
//           type: "object",
//           properties: {},
//         },
//       },
//       {
//         name: "show_toast",
//         description: "Show a toast notification in the TUI",
//         inputSchema: {
//           type: "object",
//           properties: {
//             message: {
//               type: "string",
//               description: "The message to display",
//             },
//             variant: {
//               type: "string",
//               enum: ["info", "success", "warning", "error"],
//               description: "The variant of the toast",
//             },
//             title: {
//               type: "string",
//               description: "Optional title for the toast",
//             },
//           },
//           required: ["message", "variant"],
//         },
//       },
//       {
//         name: "execute_command",
//         description: "Execute a command in the TUI",
//         inputSchema: {
//           type: "object",
//           properties: {
//             command: {
//               type: "string",
//               description: "The command to execute (e.g., agent_cycle)",
//             },
//           },
//           required: ["command"],
//         },
//       },
//       {
//         name: "get_next_event",
//         description: "Get the next event from the TUI event stream",
//         inputSchema: {
//           type: "object",
//           properties: {},
//         },
//       },
//     ],
//   };
// });

// server.setRequestHandler("tools/call", {}, async (request) => {
//   const { name, arguments: args } = request.params;
//   try {
//     switch (name) {
//       case "append_prompt":
//         await client.tui.appendPrompt({ body: { text: args.text } });
//         return { content: [{ type: "text", text: "Prompt appended successfully" }] };
//       case "submit_prompt":
//         await client.tui.submitPrompt();
//         return { content: [{ type: "text", text: "Prompt submitted successfully" }] };
//       case "clear_prompt":
//         await client.tui.clearPrompt();
//         return { content: [{ type: "text", text: "Prompt cleared successfully" }] };
//       case "show_toast":
//         await client.tui.showToast({ body: { message: args.message, variant: args.variant, title: args.title } });
//         return { content: [{ type: "text", text: "Toast shown successfully" }] };
//       case "execute_command":
//         await client.tui.executeCommand({ body: { command: args.command } });
//         return { content: [{ type: "text", text: "Command executed successfully" }] };
//       case "get_next_event":
//         if (eventQueue.length > 0) {
//           const event = eventQueue.shift();
//           return { content: [{ type: "text", text: JSON.stringify(event) }] };
//         } else {
//           return { content: [{ type: "text", text: "No event available" }] };
//         }
//       default:
//         throw new Error(`Unknown tool: ${name}`);
//     }
//   } catch (error) {
//     return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true };
//   }
// });

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("MCP TUI controller server running");