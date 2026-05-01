const errorQueue = [];

/* Wrapper function to convert generic errors into ones that work for response errors */
export function postErrorMessage(status, title, description) {
    const err = {
        status: status,
        statusText: title,
        url: description
    }
    postError(err);
}

export function postError(response) {
    // Get the type of error based on status code
    let type;
    const status = response.status;
    if (status >= 400) {
        type = "error";
    } else if (status >= 300) {
        type = "warning";
    } else if (status >= 200) {
        type = "success";
    } else {
        type = "info";
    }

    errorQueue.push({
        timestamp: Date.now(),
        statusCode: status,
        statusText: response.statusText,
        url: response.url,
        type: type
    });

    renderErrors();
}

export function renderErrors() {
    let container = document.getElementById("error-container");

    while (errorQueue.length > 0) {
        const err = errorQueue.shift();

        const toast = document.createElement("div");
        toast.className = `error-toast ${err.type}`;

        toast.innerHTML = `
            <strong>${err.statusCode}</strong> - <strong>${err.statusText}</strong>
            <div class="error-url">${err.url}</div>
        `;

        container.prepend(toast);

        setTimeout(() => {
            toast.classList.add("fade-out");

            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 4000);
    }
}