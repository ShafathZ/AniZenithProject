let messages = [];

export function addMessage({ role, content }) {
    messages.push({ role: role, content: content});
}

export async function requestAssistantMessage({ role, content }) {
    addMessage({ role: role, content: content });

    const payload = {
        "messages": messages,
        "use_local": false
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