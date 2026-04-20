import { messages } from "./chat_utils.js";
import { updateButtons } from "./chatbot_buttons.js";

const chatBox = document.getElementById("chatBox");

export function renderMessages() {
  chatBox.innerHTML = "";
  messages.forEach((msg, index) => appendUIMessage(msg, index));
  updateButtons();
}

export function appendUIMessage({ role, content }, index) {
  const messageElement = createMessageElement({ role, content }, index);
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

export function createMessageElement({ role, content }, index) {
  // Select the correct template
  const templateId = role === "assistant" ? "tmpl-assistant-message" : "tmpl-user-message";
  const template = document.getElementById(templateId);
  const messageUI = template.content.cloneNode(true);

  const messageDiv = messageUI.querySelector(".message");
  messageDiv.dataset.index = index;

  const textDiv = messageUI.querySelector(".text");

  if (role === "assistant") {
    if (content === "__thinking__") {
      textDiv.innerHTML = `
        <span class="thinking-text">
          Thinking<span class="dots"></span>
        </span>
      `;
    } else {
      textDiv.innerHTML = marked.parse(content);
    }
  } else {
    textDiv.textContent = content;
  }

  // Convert the template into live node
  const finalNode = messageUI.firstElementChild;
  return finalNode;
}

export function addDefaultMessage() {
  const defaultMessage = "Hi there! I am a friendly chatbot from Aniℤenith here to help find and recommend any anime you want! Just tell me some of your preferences, and I can help you accordingly!";
  appendUIMessage({ role: "assistant", content: defaultMessage }, messages.length);
}