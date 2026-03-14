async function loadAuthStatus() {
    try {
        // Request authentication status independently from backend. Update the page if it is found
        const response = await fetch("/proxy/auth/status");
        if (!response.ok) throw new Error("Failed to fetch auth status");

        const authStatus = await response.json();

        // Update login/logout button visibility
        const loginButton = document.querySelector(".mal-login");
        const logoutButton = document.querySelector(".mal-logout");

        if (authStatus.auth_tokens?.mal) {
            if (loginButton) loginButton.style.display = "none";
            if (logoutButton) logoutButton.style.display = "block";
        } else {
            if (loginButton) loginButton.style.display = "block";
            if (logoutButton) logoutButton.style.display = "none";
        }
    } catch (err) {
        console.warn("Could not fetch auth status:", err);
        // Re-display the login button if failed
        const loginButton = document.querySelector(".mal-login");
        if (loginButton) loginButton.style.display = "block";
    }
}


function setupOAuthLoginButton() {
    const loginButton = document.querySelector(".mal-login");
    if (!loginButton) return;

    loginButton.addEventListener("click", async () => {
        try {
            // 1. Check if backend is active for successful redirect via HEAD
            const healthCheck = await fetch("/proxy/login/mal", {
                method: "HEAD"
            });

            if (!healthCheck.ok) {
                alert("Login service is unavailable. Please try again later.");
                return;
            }

            // 2. Backend active, perform href via proxy redirect
            window.location.href = "/proxy/login/mal";
        } catch (err) {
            console.error("Backend is down:", err);
            alert("Login service is unavailable. Please try again later.");
        }
    });
}

function setupOAuthLogoutButton() {
    const logoutButton = document.querySelector(".mal-logout");
    if (!logoutButton) return;

    logoutButton.addEventListener("click", async (event) => {
        // User confirmation before logging out
        const confirmed = window.confirm("Are you sure you want to log out from MAL? App features may be limited.");
        if (!confirmed) {
            event.preventDefault();
            return;
        }

        try {
            // Send POST request for logout
            const response = await fetch("/proxy/logout/mal", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            if (response.ok) {
                // Reload page on successful logout
                window.location.reload();
            } else {
                const data = await response.json();
                alert("Logout failed: " + (data.error || "Unknown error"));
            }
        } catch (err) {
            console.error("Logout error:", err);
            alert("Logout failed. Please try again.");
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadAuthStatus();
    setupOAuthLoginButton();
    setupOAuthLogoutButton();
});