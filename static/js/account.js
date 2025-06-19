window.onload = function() {
    const container = document.getElementById("accountContainer");

    if (isLoggedIn()) {
        container.innerHTML = `<p>Welcome, ${getUserName()}!</p>`;
    } else {
        renderLoginOrRegisterForm(container);
    }
};

async function register(event) {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const username = document.getElementById("newUsername").value;
    const age = document.getElementById("age").value;
    const disabled = "false";
    const password = document.getElementById("newPassword").value;

    try {
        const response = await fetch(apiUrl("/owners"), {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: JSON.stringify({
                name,
                username,
                age,
                disabled,
                password
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Registration failed");
        }

        alert("Account created! Please log in.");
        window.location.reload(); // or redirect to login view
    } catch (error) {
        alert("Error: " + error.message);
    }
}

function renderLoginOrRegisterForm(container) {
    container.innerHTML = `
        <div class="loginPanel">
            <h2>The account management form requires a login</h2>
            <form onsubmit="login(event)">
                <input type="text" id="username" placeholder="Username" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p>Don't have an account?</p>
            <button onclick="showRegistrationForm()">Create Account</button>
        </div>
    `;
}

function showRegistrationForm() {
    const container = document.getElementById("accountContainer");
    container.innerHTML = `
        <div class="registerPanel">
            <h2>Create a TrainWeb Account</h2>
            <p>All data recorded in the below form will be recorded in our database. Although the admins of TrainWeb have made their best efforts to secure the site, nasty people will still try to hack in and steal the data.</p>
            <p>Therefore, the TrainWeb admins recommend you "spoof" any information you deem sensitive.</p>
            <form onsubmit="register(event)">
                <input type="text" id="name" placeholder="Name" required> Your full name - use this field as a means to tell us how you'd like us to identify you</input><br/>
                <input type="text" id="newUsername" placeholder="Username" required> This isn't a secured field, so you can go basic, but it must be unique</input><br/>
                <input type="age" id="age" placeholder="Age">  This isn't required, so leave blank or make it up if it makes you feel better</input><br/>
                <input type="password" id="newPassword" placeholder="Password" required>  This is important and must be secured by you (if lost, you can only reset)</input><br/>
                <button type="submit">Register</button>
            </form>
            <button onclick="window.location.reload()">Back to Login</button>
        </div>
    `;
}