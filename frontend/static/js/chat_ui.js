import { messages } from "./chat_utils.js"
import { updateButtons } from "./buttons.js"

// Render function that uses messages list internally to render page messages
export function renderMessages() {
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML = "";

    messages.forEach((msg, index) => {
        const messageElement = createMessageElement(msg, index);
        chatBox.appendChild(messageElement);
    });

    chatBox.scrollTop = chatBox.scrollHeight;
    updateButtons();
}

function createMessageElement({ role, content }, index) {
    const messageUI = document.createElement("div");
    messageUI.classList.add("message", role);
    messageUI.dataset.index = index;

    const row = document.createElement("div");
    row.classList.add("message-row");

    const avatar = document.createElement("img");
    avatar.classList.add("avatar", "no-select");
    avatar.src = role === "assistant"
        ? "/static/images/assistant.jpg"
        : "/static/images/user.jpg";
    avatar.alt = role === "assistant" ? "Assistant" : "User";

    const textDiv = document.createElement("div");
    textDiv.classList.add("text");

    if (role === "assistant") {
        textDiv.innerHTML = marked.parse(content);
        row.appendChild(avatar);
        row.appendChild(textDiv);
    } else {
        textDiv.textContent = content;
        row.appendChild(textDiv);
        row.appendChild(avatar);
    }

    messageUI.appendChild(row);

    const actions = document.createElement("div");
    actions.classList.add("actions");

    if (role === "assistant") {
        actions.innerHTML = `
            <span class="action-btn refresh"><i class="fas fa-sync-alt"></i></span>
            <span class="action-btn copy"><i class="fas fa-copy"></i></span>
            <span class="action-btn share"><i class="fas fa-share-alt"></i></span>
        `;
    } else {
        actions.innerHTML = `
            <span class="action-btn edit"><i class="fas fa-pen"></i></span>
            <span class="action-btn copy"><i class="fas fa-copy"></i></span>
            <span class="action-btn trash"><i class="fas fa-trash-alt"></i></span>
        `;
    }

    messageUI.appendChild(actions);

    return messageUI;
}