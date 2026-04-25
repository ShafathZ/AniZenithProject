import { syncMessages } from "./chat_utils.js"
import { renderMessages, appendUIMessage, addDefaultMessage } from "./chat_ui.js"
import { postErrorMessage } from "./error.js"

document.addEventListener("DOMContentLoaded", async () => {
    const userInput = document.getElementById("userInput");
    const submitButton = document.querySelector(".submit-button");

    // Add keydown event to user input
    userInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            // Allow shift-enter
            if (event.shiftKey) {
                return;
            // Hitting enter is alternate submit
            } else {
                event.preventDefault();
                submitButton.click();
            }
        }
    });

    // Sync database and then render
    const messages = await syncMessages();
    renderMessages();

    // Add default message if none are loaded
    if (messages.length === 0) {
        addDefaultMessage();
        postErrorMessage(100, "Starting Fresh Chat", "We are starting a fresh chat.");
    }
});