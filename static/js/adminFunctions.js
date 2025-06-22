const container = document.getElementById("mainAdminContainer");
console.log("Admin script was loaded successfully");
renderFetchUser(container);

function renderFetchUser(container) {
    container.innerHTML = `
        <div class="mainAdminContainer">
            <h2>Admin home</h2>
            <p>Fetch a user to open the main admin panel or fetch all users to see all users.</p>
            <form id="adminChooseUser">
                <input type="number" id="ownerId" placeholder="ownerId" required>
                <button id="submitUserId" type="submit">Fetch</button>
            </form>
            
            <br/>

            <button id="showUserTableBtn">Fetch all users</button>
        </div>
    `;

    const admimChoose = document.getElementById("adminChooseUser");
    admimChoose.addEventListener("submit", adminChosenUser);

    const showUserButton = document.getElementById("showUserTableBtn");
    showUserButton.addEventListener("click", showUserTableButt);
}

function renderAdminPanel(
    container,
    currentUser,
    userPermissions
) {

    const userData = currentUser
    const userPerm = userPermissions

    container.innerHTML = `
        <div class="mainAdminContainer">
            <h2>Manage ${userData.name}'s Account</h2>
            <p>Administration works on a system of trust. <strong>These features will be removed if abused.</strong></p>
            <div class="subAdminDetailsContainer">
                <h2>Manage details</h2>
                <p>Passwords cannot be retreived and must be reset if lost.</p>
                <p>It is good practice to support users by resetting to a generic password, getting them to log in with it, and then change to a new password.</p>
                <form id="adminAccountChanges" data-owner-id="${userData.ownerId}">
                    <input type="text" id="adminEditName" placeholder="${userData.name}"><br/>        
                    <input type="text" id="adminEditUsername" placeholder=${userData.username}><br/>
                    <input type="number" id="adminEditAge" placeholder=${userData.age || "N/A"}><br/>
                    <input type="password" id="adminEditPassword" placeholder="New Password"><br/><br/>
                    <button type="submit">Save Changes</button>
                </form>
            </div>

            <br/>

            <div class="subAdminPermContainer">
                <h2>Manage permissions</h2>
                <p>Permissions manage user access around the site. It is important all users have either the Standard permission or the Read Only permission.</p>
                <p>The Read Only permission covers the most basic of access.</p>
                <p>The Standard permission allows the same access as Read Only as well as the right to manage their Inventory (therefore both do not need to be checked if Standard is active)</p>
                <p>The Admin permission is naturally the most important, and grants the user the same user management rights as what you are utilising now. It therefore should be respected.</p>

                <form id="submitAdminPermChanges" data-owner-id="${userData.ownerId}">
                    <input type="checkbox" id="editReadOnly" data-read-only="${userPerm.readOnly}" ${userPerm.readOnly ? "checked" : ""}> Read Only<br/>
                    <input type="checkbox" id="editOwnerPerm" data-owner-perm="${userPerm.ownerPerm}" ${userPerm.ownerPerm ? "checked" : ""}> Standard<br/>
                    <input type="checkbox" id="editAdmin" data-admin="${userPerm.admin}" ${userPerm.admin ? "checked" : ""}> Admin<br/><br/>
                    <button type="submit">Save Changes</button>
                </form>         
            </div>

            <br/>

            <div class="subAdminDeleteContainer">
                <h2>Delete user</h2>
                <p>This function deletes the user, but not their inventory. The delete is irrevesible. In the event of an accident, the user will have to generate a new profile.</p>
                <p>Therefore, <strong>this function must only be used as a last resort.</strong></p>
                <p>It is better to turn off all permissions or only allow the user the Read Only permission to effectively disable a user instead.</p>
                <button id="adminDeleteUser" data-owner-id="${userData.ownerId}">Delete ${userData.name}'s profile</button>
            </div>

            <br/><button id="goBackButt">Go back</button>

        </div>
    `;

    const formAccountDetailsChange = document.getElementById("adminAccountChanges");
    formAccountDetailsChange.addEventListener("submit", submitAdminAccountChanges);

    const buttonPermChange = document.getElementById("submitAdminPermChanges");
    buttonPermChange.addEventListener("submit", submitAdminPermChanges);

    const buttonDeleteUser = document.getElementById("adminDeleteUser");
    buttonDeleteUser.addEventListener("click", submitAdminDelete);

    const adminGoBack = document.getElementById("goBackButt");
    adminGoBack.addEventListener("click", () => renderFetchUser(container));    

}

// Placeholder functions to prevent runtime errors
// function adminChooseUser(event) {
//     event.preventDefault();
//     console.log("adminChooseUser was called");
// }

async function showUserTableButt(event) {
    event.preventDefault();
    console.log("showUserTableButt was called");
    const container = document.getElementById("mainAdminContainer");

    //CALLS THE ENDPOINT
    try {
            const response = await fetch(apiUrl(`/owners`), {
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                }
            });

            if (!response.ok) {
                throw new Error("Failed to load user table");
            }

            // CAPTURE RETURNED DATA
            const usersData = await response.json();

            // SUCCESS AND ACTIVATE FORM HERE
            return console.log("Table returned:", usersData), renderUsersTable(container, usersData);

        } catch (error) {
            alert("Error loading table, info: " + error.message);
            renderFetchUser(container);
        }
}

async function renderUsersTable(container, userData) {
    const users = Array.isArray(userData) ? userData : [userData];

    if (!users.length) {
        container.innerHTML = "<p>No users were found.</p>";
        return;
    }

    let rowsHtml = users.map(user => `
        <tr>
            <td>${user.ownerId}</td>
            <td>${user.name}</td>
            <td>${user.username}</td>
            <td>${user.age ?? "N/A"}</td>
        </tr>
    `).join("");

    container.innerHTML = `
        <div class="usersTable">
            <h2>All users</h2>
            <p>The table below lists all users. Make note of the user Id of the user profile you need to manage.</p>

                <table class="userTable">
                    <thead>
                        <tr>
                            <th>User Id</th>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Age</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>

            <br/><button onclick="window.location.reload()">Go back</button>
        </div>
    `;
}

async function adminChosenUser(event) {
    event.preventDefault();
    console.log("User data pull was started");

    const ownerId = document.getElementById("ownerId").value;

    //CALLS THE ENDPOINT
    try {
            const response = await fetch(apiUrl(`/owners/admin/${ownerId}`), {
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                }
            });

            // OLD ERROR LOGIC
            // if (!response.ok) {
            //     throw new Error("Failed to load account details");
            // }
            if (!response.ok) {
                let errorMessage = "Failed to load account details";
                try {
                    const errorData = await response.json();
                    if (errorData?.detail) {
                        errorMessage = errorData.detail;
                    }
                } catch (e) {
                    //FAILED TO PASS ERROR
                }
                throw new Error(errorMessage);
            }

            // CAPTURE RETURNED DATA
            const userData = await response.json();
            const currentUser = userData.user;
            const userPermissions = userData.permissions;

            return renderAdminPanel(
                container, currentUser, userPermissions
            );

        } catch (error) {
            alert("Error loading account info: " + error.message);
            renderFetchUser(container);
        }
}

async function submitAdminAccountChanges(event) {
    event.preventDefault();
    console.log("Details are now being submitted.");

    const dataForm = document.getElementById("adminAccountChanges");
    const ownerId = dataForm.dataset.ownerId;

    const adminName = document.getElementById("adminEditName").value.trim();
    const adminUsername = document.getElementById("adminEditUsername").value.trim();
    const adminAge = document.getElementById("adminEditAge").value.trim();
    const adminPassword = document.getElementById("adminEditPassword").value.trim();

   
    const body = {};
        if (adminName) body.name = adminName;
        if (adminUsername) body.username = adminUsername;
        if (adminAge) body.age = Number(adminAge);
        if (adminPassword) body.password = adminPassword;
        
    if (Object.keys(body).length == 0) {
        alert("Please fill in at least one field to update");
        return;
    }

    try {
        const response = await fetch(apiUrl(`/owners/admin/${ownerId}`), {
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

async function submitAdminPermChanges(event) {
    event.preventDefault();
    console.log("User permissions update was started.")

    const form = event.target;
    const ownerId = form.getAttribute("data-owner-id");

    // FETCH THE CHECKED ELEMENTS
    const readOnlyCheckbox = form.querySelector("#editReadOnly");
    const ownerPermCheckbox = form.querySelector("#editOwnerPerm");
    const adminCheckbox = form.querySelector("#editAdmin");

    // READ THE CURRENT STATES
    const currentReadOnly = readOnlyCheckbox.checked;
    const currentOwnerPerm = ownerPermCheckbox.checked;
    const currentAdmin = adminCheckbox.checked;

    // READ THE ORIGINALS FROM THE DATA ATTRIBUTES
    const originalReadOnly = readOnlyCheckbox.getAttribute("data-read-only") === "true";
    const originalOwnerPerm = ownerPermCheckbox.getAttribute("data-owner-perm") === "true";
    const originalAdmin = adminCheckbox.getAttribute("data-admin") === "true";

    // COMPARE FOR CHANGES
    const hasChanges =
        currentReadOnly !== originalReadOnly ||
        currentOwnerPerm !== originalOwnerPerm ||
        currentAdmin !== originalAdmin;

    if (!hasChanges) {
        alert("No changes detected.");
        return;
    }

    // BUILD THE PAYLOAD FOR ANY CHANGES
    const updatePayload = {};
    if (currentReadOnly !== originalReadOnly) updatePayload.readOnly = currentReadOnly;
    if (currentOwnerPerm !== originalOwnerPerm) updatePayload.ownerPerm = currentOwnerPerm;
    if (currentAdmin !== originalAdmin) updatePayload.admin = currentAdmin;

    // Submit patch request
    try {
        const response = await fetch(apiUrl(`/perm/${ownerId}`), {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
            },
            body: JSON.stringify(updatePayload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Failed to update permissions.");
        }

        alert("Permissions updated successfully.");
    } catch (err) {
        alert("Error updating permissions: " + err.message);
    }
}

async function submitAdminDelete() {
    const confirmDelete = confirm("Are you sure you want to delete this user's account? This action cannot be undone. By proceeding you also understand you will lose admin privaledges if misused?");
    if (!confirmDelete) return;

    console.log("User delete has started");

    const dataButton = document.getElementById("adminAccountChanges");
    const ownerId = dataButton.dataset.ownerId;

    try {
        // CALL THE FIRST ENDPOINT TO DELETE PERMISSIONS
        const permResponse = await fetch(apiUrl(`/perm/${ownerId}`), {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`
            }
        });

        if (!permResponse.ok) {
            const err = await permResponse.json();
            throw new Error(err.detail || "Failed to delete permissions");
        }
    
        // CALL THE SECOND ENDPOINT TO DELETE USER
        const response = await fetch(apiUrl(`/owners/${ownerId}`), {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`
            }
        });

        // ERROR CAPTURE
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Delete failed");
        }

        // SUCCESS
        alert("Account deleted.");
        window.location.reload();

    } catch (error) {
        alert("Error: " + error.message);
    }
}