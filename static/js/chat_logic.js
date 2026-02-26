export let messages = [];
let useLocalModel = false;

export function setLocalModelStatus(local) {
    useLocalModel = local;
}

export function addMessage({ role, content }) {
    messages.push({ role: role, content: content});
    return messages.length - 1;
}

export function deleteMessage(index) {
    messages.splice(index);
    return true;
}

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
    try {
        const response = await fetch("http://localhost:4007/anizenith/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        // Handle non-200 responses
        if (!response.ok) {
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