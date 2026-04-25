import { messages } from "./chat_utils.js"
import { updateButtons } from "./buttons.js"

const chatBox = document.getElementById("chatBox");

// Render function that uses messages list internally to render page messages
export function renderMessages() {
    chatBox.innerHTML = "";
    // Add all messages from message store
    messages.forEach((msg, index) => {appendUIMessage(msg, index);});
    updateButtons();
}

export function appendUIMessage({ role, content }, index) {
    // Construct the element
    const messageElement = createMessageElement({ role, content }, index);

    // Add it to UI box
    chatBox.appendChild(messageElement);

    // Scroll if needed
    chatBox.scrollTop = chatBox.scrollHeight;
}

export function createMessageElement({ role, content }, index) {
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
        // Add UI tag for thinking
        if (content === "__thinking__") {
            textDiv.innerHTML = `
                <span class="thinking-text">
                    Thinking<span class="dots"></span>
                </span>
            `;
        } else {
            textDiv.innerHTML = marked.parse(content);
        }
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

export function addDefaultMessage() {
    const defaultMessage = "Hi there! I am a friendly chatbot from Aniℤenith here to help find and recommend any anime you want! Just tell me some of your preferences, and I can help you accordingly!"
    appendUIMessage({ role: "assistant", content: defaultMessage }, messages.length);
}