// window.onload = function() {
//     const container = document.getElementById("accountContainer");

//     if (isLoggedIn()) {
//         renderAccountView();
//     } else {
//         renderLoginOrRegisterForm(container);
//     }
// };

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("accountContainer");

    if (isLoggedIn()) {
        loadAccountDetails(container);
    } else {
        renderLoginOrRegisterForm(container);
    }
});

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
                "Content-Type": "application/json"
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
        window.location.href = "/account";
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

function renderAccountView(containerId = "accountContainer", userData) {
    const container = document.getElementById(containerId);
    if (!container || !userData) return;

    container.innerHTML = `
    <div class="accountManager">
        <h2>Welcome, ${userData.name}</h2>
        <p><strong>Name:</strong> ${userData.name}</p>
        <p><strong>Username:</strong> ${userData.username}</p>
        <p><strong>Age:</strong> ${userData.age || "N/A"}</p></b>
        <p>Your password can be changed in the edit form</p>

        <button onclick="showEditAccountForm()">Edit Details</button>
        <button onclick="deleteAccount()">Delete Account</button>
        <button onclick="logout()">Logout</button>
    </div>
    `;
}

function showEditAccountForm() {
    const container = document.getElementById("accountContainer");

    container.innerHTML = `
        <div class="accountManager">
            <h2>Edit Account</h2>
            <p>Update any of your details in the form below then click "save changes" to update them.</p>
            <p>Only filled fields will be updated.</p>
            <form onsubmit="submitAccountChanges(event)">
                <input type="text" id="editName" placeholder="Name"><br/>        
                <input type="text" id="editUsername" placeholder="Username (must be unique)"><br/>
                <input type="number" id="editAge" placeholder="Age (optional)"><br/>
                <input type="password" id="editPassword" placeholder="New Password"><br/>
                <button type="submit">Save Changes</button>
            </form>
            <button onclick="window.location.reload()">Cancel</button>
        <div>
    `;
}

async function submitAccountChanges(event) {
    event.preventDefault();

    const name = document.getElementById("editName").value.trim();
    const username = document.getElementById("editUsername").value.trim();
    const age = document.getElementById("editAge").value.trim();
    const password = document.getElementById("editPassword").value.trim();

   
    const body = {};
        if (name) body.name = name;
        if (username) body.username = username;
        if (age) body.age = Number(age);
        if (password) body.password = password;
        
    if (Object.keys(body).length == 0) {
        alert("Please fill in at least one field to update");
        return;
    }

    try {
        const response = await fetch(apiUrl("/owners/me"), {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Update failed");
        }

        alert("Account updated successfully.");
        window.location.reload();
    } catch (error) {
        alert("Error: " + error.message);
    }
}

async function deleteAccount() {
    const confirmDelete = confirm("Are you sure you want to delete your TrainWeb account? This action cannot be undone.");
    if (!confirmDelete) return;

    try {
        const response = await fetch(apiUrl("/user/me"), {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`
            }
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Delete failed");
        }

        alert("Account deleted.");
        logoutUser();
        window.location.reload();
    } catch (error) {
        alert("Error: " + error.message);
    }
}

async function loadAccountDetails() {
    try {
            const response = await fetch(apiUrl(`/user/me`), {
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                }
            });

            if (!response.ok) {
                throw new Error("Failed to load account details");
            }

            const userData = await response.json();
            renderAccountView("accountContainer", userData);
        } catch (error) {
            alert("Error loading account info: " + error.message);
            renderLoginOrRegisterUI("accountContainer");
        }
}
