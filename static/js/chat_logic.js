let messages = [];

function renderMessages() {
    const chatDiv = document.getElementById("chat");
    chatDiv.innerHTML = "";

    messages.forEach(msg => {
        const div = document.createElement("div");
        div.textContent = `${msg.role}: ${msg.content}`;
        chatDiv.appendChild(div);
    });
}

async function sendMessage() {
    const input = document.getElementById("input");
    const userMessage = input.value;

    if (!userMessage) return;

    messages.push({ role: "user", content: userMessage });
    renderMessages();

    input.value = "";

    const response = await fetch("http://localhost:3000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ messages })
    });

    const data = await response.json();

    messages.push({ role: "assistant", content: data.reply });
    renderMessages();
}