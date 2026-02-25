let messages = [];

export function addMessage({ role, msg }) {
    messages.push({ role: role, message: msg});
}

export async function requestAssistantMessage({ role, message }) {
    addMessage({ role: role, message: message });

    try {
        const response = await fetch("http://localhost:3000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ messages })
        });

        // Handle non-200 responses
        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();
        const assistant_response = { role: "assistant", message: data.message };

        addMessage(assistant_response);
        return assistant_response;

    } catch (error) {
        // Fetch throws error during connection failure / bad headers
        const failed_response = { role: "assistant", message: "Error: Failed to connect to the backend client." };

        //addMessage(failed_response);
        return failed_response;
    }
}