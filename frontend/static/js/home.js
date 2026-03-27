document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("userInput");
    const submitButton = document.querySelector(".submit-button");

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
});