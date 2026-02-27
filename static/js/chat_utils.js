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
    const payload = {
        "messages": messages,
        "use_local": useLocalModel
    }
    console.log(payload);
    try {
        const response = await fetch("/proxy/anizenith/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        // Handle non-200 responses
        // TODO: Make the response handling better for non-200 (e.g. 4XX different from 3XX or 5XX)
        if (!response.ok) {
            console.log(response);
            throw new Error("Server error");
        }

        const data = await response.json();
        const assistant_response = { role: "assistant", content: data.messages.at(-1).content };

        addMessage(assistant_response);
        return assistant_response;

    } catch (error) {
        // Fetch throws error during connection failure / bad headers
        const failed_response = { role: "assistant", content: "Error: Failed to connect to the backend client." };

        //addMessage(failed_response);
        return failed_response;
    }
}