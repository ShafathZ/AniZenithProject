import { messages, addMessage, deleteMessage, editMessage, sendMessagesToBackend } from "./chat_logic.js"
import { renderMessages } from "./chat_ui.js"

export function updateButtons() {
    // Dynamic buttons
    setupCopyButtons();
    setupShareButtons();
    setupDeleteButtons();
    setupEditButtons();
    setupRefreshButtons();
}

// Adds copy logic with small check mark to showcase it working for UX
function setupCopyButtons() {
    const copyButtons = document.querySelectorAll(".action-btn.copy");

    copyButtons.forEach(copyBtn => {
        copyBtn.onclick = () => {
            const message = copyBtn.closest(".message");
            const textDiv = message.querySelector(".text").textContent.trim();

            navigator.clipboard.writeText(textDiv)
                .then(() => {
                    copyBtn.innerHTML = '<span style="font-size: 10px;">✓</span>';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 1000);
                })
                .catch(err => console.error("Failed to copy:", err));
        };
    });
}

// Adds a click event to use built in share mechanic when clicking share icon. Shares the specific text share button was clicked on
function setupShareButtons() {
    const shareButtons = document.querySelectorAll(".action-btn.share");

    shareButtons.forEach(shareBtn => {
        shareBtn.onclick = async () => {
            const message = shareBtn.closest(".message");
            const textDiv = message.querySelector(".text").textContent.trim();

            if (navigator.share) {
                try {
                    await navigator.share({ text: textDiv });
                } catch (err) {
                    console.error("Share canceled or failed:", err);
                }
            } else {
                prompt("Web Share not supported. Copy this text to share:", textDiv);
            }
        };
    });
}

// Adds event listener to delete button to delete latest message and re-render.
function setupDeleteButtons() {
    const deleteButtons = document.querySelectorAll(".action-btn.trash");

    deleteButtons.forEach(deleteBtn => {
        deleteBtn.onclick = () => {
            const message = deleteBtn.closest(".message");
            const index = parseInt(message.dataset.index, 10);

            deleteMessage(index);
            renderMessages();
        };
    });
}

// Sets up edit functionality using contentEditable method
function setupEditButtons() {
    const editButtons = document.querySelectorAll(".action-btn.edit");

    editButtons.forEach(editBtn => {
        editBtn.onclick = () => {
            const messageEl = editBtn.closest(".message");
            const index = parseInt(messageEl.dataset.index, 10);
            const textDiv = messageEl.querySelector(".text");

            if (textDiv.isContentEditable) return;

            const originalText = textDiv.textContent;

            textDiv.contentEditable = "true";
            textDiv.classList.add("editing");
            textDiv.focus();

            // Move cursor to end
            const range = document.createRange();
            range.selectNodeContents(textDiv);
            range.collapse(false);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);

            // On edit finish, send edit to chat logic which requests new data from backend (deletes future messages)
            const finishEdit = async (save) => {
                textDiv.contentEditable = "false";
                textDiv.classList.remove("editing");
                textDiv.removeEventListener("keydown", handleKey);
                console.log("Set up event handler");

                if (!save) {
                    textDiv.textContent = originalText;
                    return;
                }

                const newText = textDiv.textContent.trim();

                if (newText === originalText || newText === "") {
                    textDiv.textContent = originalText;
                    return;
                }

                editMessage(index, newText);
                await sendMessagesToBackend();
                renderMessages();
            };

            // When to handle saying editing is done (on Enter / blur / escape)
            const handleKey = (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    textDiv.blur();
                }

                if (e.key === "Escape") {
                    e.preventDefault();
                    finishEdit(false);
                }
            };

            textDiv.addEventListener("keydown", handleKey);

            // Only blur triggers save
            textDiv.addEventListener(
                "blur",
                () => finishEdit(true),
                { once: true }
            );
        };
    });
}

// Adds click event listener to refresh button which deletes latest assistant message and then gets response again
function setupRefreshButtons() {
    const refreshButtons = document.querySelectorAll(".action-btn.refresh");

    refreshButtons.forEach(refreshBtn => {
        refreshBtn.onclick = async () => {
            const message = refreshBtn.closest(".message");
            const index = parseInt(message.dataset.index, 10);

            deleteMessage(index);
            await sendMessagesToBackend();
            renderMessages();
        };
    });
}

// Sets button click event to sendMessage function below
function setupSendButton() {
    const button = document.querySelector(".submit-button");
    button.onclick = sendMessage;
}

// Logic for when send is activated
async function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();

    if (!text) return;

    // Add the message to the UI and clear text
    const new_message = { role: "user", content: text };

    input.value = "";
    input.focus();

    addMessage(new_message);
    renderMessages();

    // Get assistant response and add it
    await sendMessagesToBackend();
    renderMessages();
}

// Converts full chat into a nice string to copy
function getFullChatText() {
    return messages
        .map(msg => {
            // Replace assistant role with AniZenith
            const roleName = msg.role === "assistant" ? "AniZenith" : msg.role;
            return `${roleName}: ${msg.content}`;
        })
        .join("\n");
}

// Share full chat via built in share method or as raw text if not
function setupShareFullChatButton() {
    const shareBtn = document.querySelector(".share-button");
    if (!shareBtn) return;

    shareBtn.addEventListener("click", () => {
        const fullText = getFullChatText();

        // Default browser share feature
        if (navigator.share) {
            navigator.share({ text: fullText }).catch(err => {
                console.error("Share failed:", err);
                alert("Sharing failed or canceled.");
            });
        } else {
            prompt("Copy the chat text to share:", fullText);
        }
    });
}

// Copy full chat as a string
function setupCopyFullChatButton() {
    const copyBtn = document.querySelector(".copy-button");
    if (!copyBtn) return;

    copyBtn.addEventListener("click", () => {
        const fullText = getFullChatText();

        // Save to clipboard with check mark indicator
        navigator.clipboard.writeText(fullText)
            .then(() => {
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<span style="font-size: 14px;">✔</span>';

                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                }, 1000);
            })
            .catch(err => {
                console.error("Copy failed:", err);
                alert("Copy failed.");
            });
    });
}

// Deletes all messages with a user confirmation box
function setupClearFullChatButton() {
    const resetBtn = document.querySelector(".reset-button");
    if (!resetBtn) return;

    resetBtn.addEventListener("click", () => {
        if (!confirm("Are you sure you want to clear the full chat?")) return;

        deleteMessage(0);
        renderMessages();
    });
}

// Basic quick suggestion function that just auto fills the input area with a preset
function setupQuickSuggestionButtons() {
    const buttons = document.querySelectorAll(".quick-suggestions button");
    const userInput = document.getElementById("userInput");
    const defaultPlaceholder = "Ask for anime recommendations...";

    userInput.placeholder = defaultPlaceholder;

    buttons.forEach(button => {
        if (button.classList.contains("add-button")) return;

        const text = button.textContent.trim();
        const hoverText = `Hi, can you recommend me some ${text} anime?`;

        button.addEventListener("mouseenter", () => {
            userInput.placeholder = hoverText;
        });

        button.addEventListener("mouseleave", () => {
            userInput.placeholder = defaultPlaceholder;
        });

        button.addEventListener("click", () => {
            userInput.value = hoverText;
            userInput.focus();
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    updateButtons();

    // Constant buttons
    setupSendButton();
    setupShareFullChatButton();
    setupCopyFullChatButton();
    setupClearFullChatButton();
    setupQuickSuggestionButtons();
});