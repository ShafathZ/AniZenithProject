import { postError } from "./error.js"

// Client-side conversation message storage (Chats are only stored on client side for now)
export let messages = [];
// JS identifier for Local model toggle
let useLocalModel = false;

// Sets if user requests local model or not from backend
export function setLocalModelStatus(local) {
    useLocalModel = local;
}

// Adds a message to conversation list. Returns the index of the message that got added
export function addMessage({ role, content }) {
    messages.push({ role: role, content: content});
    return messages.length - 1;
}

// Deletes all messages from the requested index (Preserves CausalLM chain)
export function deleteMessage(index) {
    messages.splice(index);
    return true;
}

// Edits a single message at a specific index in the conversation and deletes all future messages (Preserves CausalLM chain)
export function editMessage(index, newContent) {
    messages[index].content = newContent;
    messages.splice(index + 1);
    return true;
}

export async function sendMessagesToBackend() {
    // Construct payload for frontend service
    const payload = {
        "messages": messages,
        "use_local": useLocalModel
    }

    try {
        // If using local, detect and add additional timeout
        const timeout = payload.use_local ? 180.0 : 5.0;
        const response = await fetch("/proxy/anizenith/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Request-Timeout": timeout.toString()
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const err = new Error(response.statusText);
            err.response = response;
            throw err;
        }

        const data = await response.json();
        const assistant_response = { role: "assistant", content: data.messages.at(-1).content };
        return assistant_response;

    } catch (error) {
        // Fetch throws error during connection failure / bad headers
        const response = error.response;
        const failed_response = { role: "assistant", content: "Error: Failed to connect to the backend client." };
        postError(error.response);
        return failed_response;
    }
}