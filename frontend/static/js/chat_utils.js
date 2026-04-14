import { postError, postErrorMessage } from "./error.js"
import { pushMessages, pullMessages } from "./chat_history_db.js";

// Client-side conversation message storage (Chats are only stored on client side for now)
export let messages = [];
// JS identifier for Local model toggle
let useLocalModel = false;

// Internal validation function to ensure messages was not corrupted in cache
function isValid(messages) {
    if (!Array.isArray(messages)) return false;
    if (messages.length === 0) return true;

    // 1. First must be user
    if (messages[0].role !== "user") return false;

    // 2. Last must be assistant
    if (messages[messages.length - 1].role !== "assistant") return false;

    // 3. Must alternate roles
    for (let i = 1; i < messages.length; i++) {
        if (messages[i].role === messages[i - 1].role) {
            return false;
        }
    }

    return true;
}

// Syncs messages in RAM with Client DB stored messages
export async function syncMessages() {
    messages = await pullMessages(); // Pulls messages in async context

    // Validate synced messages (in case of corrupted cache)
    if (!isValid(messages)) {
        postErrorMessage(500, "Corrupted History", "Chat history was corrupted and reset.")
        messages = []; // Make messages empty (reset)
    }

    return messages;
}

// Sets if user requests local model or not from backend
export function setLocalModelStatus(local) {
    useLocalModel = local;
}

// Adds a message to conversation list. Returns the index of the message that got added
export function addMessage({ role, content }) {
    const msg = { role, content };

    // 1. Update RAM-stored message list
    messages.push(msg);

    // 2. Send to DB to store new state -- Not in async
    pushMessages(messages).catch(err => {
        console.error("Failed to sync Chat Log DB:", err);
    });

    return messages.length - 1;
}

// Deletes all messages from the requested index (Preserves CausalLM chain)
export function deleteMessage(index) {
    // 1. update RAM
    messages.splice(index);

    // 2. Send to DB to store new state -- Not in async
    pushMessages(messages).catch(err => {
        console.error("Failed to sync Chat Log DB:", err);
    });

    return true;
}

// Edits a single message at a specific index in the conversation and deletes all future messages (Preserves CausalLM chain)
export function editMessage(index, newContent) {
    // 1. update RAM
    messages[index].content = newContent;
    messages.splice(index + 1);

    // 2. Send to DB to store new state -- Not in async
    pushMessages(messages).catch(err => {
        console.error("Failed to sync Chat Log DB:", err);
    });

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
        const timeout = payload.use_local ? 180.0 : 25.0;
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