function addMessage({ role, msg }) {

    console.log(msg);

    const chatBox = document.getElementById("chatBox");

    // Create message container
    const message = document.createElement("div");
    message.classList.add("message", role);

    // Create message row
    const row = document.createElement("div");
    row.classList.add("message-row");

    // Add image of avatar
    const avatar = document.createElement("img");
    avatar.classList.add("avatar", "no-select");
    avatar.src = role === "bot" ? "/static/images/bot.jpg" : "/static/images/user.jpg";
    avatar.alt = role === "bot" ? "Bot" : "User";

    // Add message
    const textDiv = document.createElement("div");
    textDiv.classList.add("text");
    textDiv.textContent = msg;

    // Combine into the row in correct order
    if (role === "bot") {
        row.appendChild(avatar);
        row.appendChild(textDiv);
    } else {
        row.appendChild(textDiv);
        row.appendChild(avatar);
    }
    message.appendChild(row);

    // Create actions section
    const actions = document.createElement("div");
    actions.classList.add("actions");

    // Add buttons based on which role / side of conversation
    if (role === "bot") {
        actions.innerHTML = `
            <span class="action-btn refresh" title="Refresh"><i class="fas fa-sync-alt"></i></span>
            <span class="action-btn copy" title="Copy"><i class="fas fa-copy"></i></span>
            <span class="action-btn share" title="Share"><i class="fas fa-share-alt"></i></span>
        `;
    } else {
        actions.innerHTML = `
            <span class="action-btn edit" title="Edit"><i class="fas fa-pen"></i></span>
            <span class="action-btn copy" title="Copy"><i class="fas fa-copy"></i></span>
            <span class="action-btn trash" title="Delete"><i class="fas fa-trash-alt"></i></span>
        `;
    }
    message.appendChild(actions);

    // Append to chat box
    chatBox.appendChild(message);

    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // TODO: Trim the last N chat messages to avoid long chats on visual display
}

// Logic for when send is activated
function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();

    if (!text) return;

    addMessage({ role: "user", msg: text });
    input.value = "";

    input.focus();
}