function apiUrl(path) {
    return `${window.location.origin}${path}`;
}

function goToRegister() {
    window.location.href = "/account";
}

function isLoggedIn() {
    return localStorage.getItem("accessToken") !== null;
}

function getUsername() {
    return localStorage.getItem("username");
}

function renderLoggedInUI() {
    const user = getUsername();
    return `
        <div class="loginBar">Welcome, <strong>${user}</strong>!
            <button onclick="logout()">Logout</button>
        </div>
    `;
}

function renderLoginUI() {
    return `
        <div class="loginBar">
            <form onsubmit="login(event)">
                <input type="text" id="username" placeholder="Username" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    `;
}

function renderCreateAccountUI() {
    return `
        <div class="loginBar">
            <button onclick="goToRegister()">Register</button>
        
    `;
}

function renderLoginOrRegisterUI() {
    const container = document.getElementById("loginContainer");

    let html = "";

    if (!isLoggedIn()) {
        html = `
            <div class="authRow">
                ${renderLoginUI()}
                ${renderCreateAccountUI()}
            </div>
        `;
    } else {
        html += renderLoggedInUI()
    }
    
    container.innerHTML = html;
}

async function login(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(apiUrl("/token"), {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                username,
                password
            })
        });

        if (!response.ok) {
            throw new Error("Invalid credentials");
        }

        const data = await response.json();
        localStorage.setItem("accessToken", data.access_token);
        localStorage.setItem("username", username);
        renderLoginOrRegisterUI();
    } catch (error) {
        alert("Login failed: " + error.message);
    }
}

function logout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    renderLoginOrRegisterUI();
}

async function refreshAccessToken() {
    const response = await fetch(apiUrl("/refresh-token"), {
        method: "POST",
        credentials: "include"
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem("accessToken", data.access_token);
        return true;
    } else {
        logout();
        return false;
    }
}

async function authFetch(url, options = {}) {
    options.headers = options.headers || {};
    options.headers["Authorization"] = `Bearer ${localStorage.getItem("accessToken")}`;

    let response = await fetch(apiUrl(url), options);

    if (response.status === 401) {
        // TRY REFRESH
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            // RETRY THE ORIGINAL REQUEST WITH A NEW TOKEN
            options.headers["Authorization"] = `Bearer ${localStorage.getItem("accessToken")}`;
            response = await fetch(apiUrl(url), options);
        } else {
            // WHEN IT FAILS
            throw new Error("Unauthorized");
        }
    }

    return response;
}

window.onload = renderLoginOrRegisterUI;