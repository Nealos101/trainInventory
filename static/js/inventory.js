document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("inventoryContainer");

    if (isLoggedIn()) {
        inventoryStartup(container);
    } else {
        renderLoginReminder(container);
    }
});

function renderLoginReminder(container) {

    container.innerHTML=`
    <div class="mainAdminContainer">
        <h2>Not logged in</h2>
        <p>This function requires a TrainWeb account.</p><br/>

        <button id="invLoginButt">Login or Register</button>
    </div>
    `;

    const invLoginClick = document.getElementById("invLoginButt");
    invLoginClick.addEventListener("click", function () {
        redirectTo(paths.acc);
    });

}

async function inventoryStartup(container) {

    try {
        const { currentUser, userPermissions} = await retrieveUserDetails()

        //CHECKS IF THE USER IS AN ADMIN, IF SO CALLS THE ADMIN SCRIPT
        if (userPermissions?.admin) {
            const script = document.createElement("script");
            script.src = "/static/js/inventoryAdmin.js";
            script.type = "module"
            document.head.appendChild(script);
        }

        loadInventoryLanding(
            container, {
                user: currentUser
            }
        );
      
    } catch (error) {
        alert("Error loading table, info: " + error.message);
    }
}

async function loadInventoryLanding(container, currentUser) {
    const invOwner = currentUser.user.ownerId

    //CALLS THE ENDPOINT
    try {
        const invResponse = await fetch(apiUrl(`/inventory/${invOwner}`), {
            headers: {
                            "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                        }
                    });
    
        if (!invResponse.ok) {
            let errorMessage = "Failed to load inventory";
            try {
                const errorData = await invResponse.json();
                if (errorData?.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                //FAILED TO PASS ERROR
            }
            throw new Error(errorMessage);
        }

        //CAPTURE RETURNED DATA
        const invData = await invResponse.json();
        console.log(invData);

        return loadedInventoryLanding(
            container, invData, invOwner
        );

    } catch (error) {
        alert("Error loading inventory: " + error.message);
        unloadedInventoryLanding(container, invOwner);
    }
}

async function loadedInventoryLanding(container, invData, invOwner) {
    const inventory = Array.isArray(invData) ? invData : [invData];

    if (!inventory.length) {
        return unloadedInventoryLanding(container, invOwner);
    }

    let rowsHtml = inventory.map(inv =>`
        <tr>
            <td>${inv.clientId}</td>
            <td>${inv.stockBrand}</td>
            <td>${inv.stockName}</td>
            <td>${inv.stockRoadNumber}</td>
            <td>${inv.stockComments}</td>
            <td>
                <button class="viewBtn" data-id="${inv.invId}">View</button>
            </td>
        </tr>
    `).join("");

    container.innerHTML =`
        <div class="inventoryContainer" data-inv-owner="${invOwner}">
            <h2>Inventory Summary</h2>
            <p>Showing a summary of your current items stored in TrainWeb's database. Click on the buttons beside the items to navigate, or click on the button below to create a new record.</p>

                <table class="inventoryTable">
                    <thead>
                        <tr>
                            <th>Your Stock Id</th>
                            <th>Brand</th>
                            <th>Name</th>
                            <th>Roadnumber</th>
                            <th>Comments</th>
                            <th>View</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>

                <br/>

                <button id="createNewRecordButt">Create a record</button>

        </div>
    `;

    attachCreateRecordListener("createNewRecordButt", container);

    const viewButtons = container.querySelectorAll(".viewBtn");

    viewButtons.forEach(button => {
        button.addEventListener("click", async () => {
            const invId = button.dataset.id;

            try {

                const response = await fetch(apiUrl(`/inventory/${invOwner}/${invId}`), {
                    headers: {
                        "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                    }
                 });

                if (!response.ok) {
                    throw new Error("Failed to load record");
                }

                const invDetails = await response.json();

                return console.log("Details returned:", invDetails);

            } catch (error) {
                console.error("Record load failed, info: ", error.message);
            }
        });
    });
}

function unloadedInventoryLanding(container, invOwner) {

    container.innerHTML=`
        <div class="inventoryContainer" data-inv-owner="${invOwner}">
            <h2>No Inventory yet</h2>
            <p>It looks like you don't have any inventory on Trainweb yet. Ready to change that? Click the button below!</p>

                <button id="createNewRecordButt">Create a record</button>

        </div>
    `;

    attachCreateRecordListener("createNewRecordButt", container);

}

// BUTTON LISTENER FOR CREATE NEW RECORD
function attachCreateRecordListener(buttonId, container) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.addEventListener("click", () => {
            const invContainer = document.querySelector(".inventoryContainer");
            if (!invContainer) {
                console.warn("Inventory container not found.");
                return;
            }

            const ownerId = invContainer.dataset.invOwner;
            if (!ownerId) {
                console.warn("Owner Id missing from container.");
                return;
            }

            fetchEnums(container, ownerId);
        });
    }
}

// BUTTON LISTENER TO GO BACK TO MAIN INVENTORY PANEL
function attachCancelListener(buttonId, container) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.addEventListener("click", () => {
            const invContainer = document.querySelector(".inventoryContainer");
            if (!invContainer) {
                console.warn("Inventory container not found.");
                return;
            }

            const ownerId = invContainer.dataset.invOwner;
            if (!ownerId) {
                console.warn("Owner Id missing from container.");
                return;
            }

            inventoryStartup(container)

        })
    }


}

async function fetchEnums(container, ownerId) {
    console.log("Enum pull was started");

    //CALLS THE ENDPOINT
    try {
        const response = await fetch(apiUrl(`/enum/`));
        if (!response.ok) {
            throw new Error("Failed to fetch enums");
        }

        //CAPTURE RETURNED ENUMS
        const enumData = await response.json();

        console.log(enumData);
        const wheelClasses = enumData.wheelClasses;
        const couplerClasses = enumData.couplerClasses;
        const powerClasses = enumData.powerClasses;
        const stockClasses = enumData.stockClasses;

        return newInvRecordCreate(
            container, ownerId, wheelClasses, couplerClasses, powerClasses, stockClasses
        );

        } catch (error) {
            alert("Error loading enums, info: " + error.message);
            window.location.reload();
        }
}


function newInvRecordCreate(
    container, invOwner, wheelClasses, couplerClasses, powerClasses, stockClasses
) {

    container.innerHTML =` 
        <div class="inventoryContainer" data-inv-owner="${invOwner}">
            <h2>Create an Inventory Record</h2>
            <p>All data recorded in the below form will be recorded in our database. Although the admins of TrainWeb have made their best efforts to secure the site, nasty people will still try to hack in and steal the data.</p>
            <p>Therefore, the TrainWeb admins recommend you "spoof" any information you deem sensitive.</p>

            <div class="createRecordForm">
                <form onsubmit="generateInvRecord(event)">

                    <h3>Required Fields</h3>
                    <p>These fields need to be filled to create a record.</p>

                    <div class="invAddRequired">

                        <p>Identifying fields</p>

                        <input
                            type="text"
                            id="clientId"
                            placeholder="Your Stock Identifier"
                            required
                        >
                        <label for "clientId"> Must be unique to your Inventory</label><br/>

                        <input
                            type="text"
                            id="stockName"
                            placeholder="Name"
                            required
                        >
                        <label for "stockName"> Usually make and model</label><br/>

                        <input
                            type="text"
                            id="stockRoadNumber"
                            placeholder="Road number"
                        >
                        <label for "stockRoadNumber"> Designation normally found on the sides</label><br/>

                        <p>Stock Type Selector</p>

                        <select id="stockType"></select>
                        <label for "stockType"> Select the type</label><br/>
                    
                    </div>

                    <h3>Optional Fields</h3>
                    <p>These fields don't need to be filled in... Buy why wouldn't you?</p>

                    <div class="invAddOptional">

                    <p>About the Item</p>
                    
                        <input
                            type="text"
                            id="stockBrand"
                            placeholder="Manufacturer"
                        >
                        <label for "stockBrand"> Who made it</label><br/>

                        <input
                            type="text"
                            id="stockRailroad"
                            placeholder="Name of railroad"
                        >
                        <label for "stockRailroad"> Details of the owner or company found with the livery</label><br/>

                        <input
                            type="text"
                            id="stockLivery"
                            placeholder="Name of the scheme"
                        >
                        <label for "stockLivery"> The scheme (or just use descriptors)</label><br/>

                        <input
                            type="decimal"
                            id="purchaseCost"
                            placeholder="1234.00"
                        >
                        <label for "purchaseCost"> The cost, just as a number</label><br/>

                        <input
                            type="date"
                            id="purchaseDate"
                            placeholder="dd/mm/yyyy eg. 23/06/2025"
                        >
                        <label for "purchaseDate"> The date you purchased</label><br/>

                        <p>Material and Power Selectors</p>

                        <select id="stockPower"></select>
                        <label for "stockPower"> The type of power or control</label><br/>

                        <select id="stockWheelType"></select>
                        <label for "stockWheelType"> The wheels</label><br/>
                        
                        <select id="stockCouplerType"></select>
                        <label for "stockCouplerType"> The couplers</label><br/>

                        <p>Prototype tracking dates</p>

                        <input
                            type="date"
                            id="prototypeStart"
                            placeholder="dd/mm/yyyy eg. 23/06/2025"
                        >
                        <label for "prototypeStart"> The date the prototype introduced it</label><br/>

                        <input
                            type="date"
                            id="prototypeEnd"
                            placeholder="dd/mm/yyyy eg. 23/06/2025"
                        >
                        <label for "prototypeEnd"> The date when the prototype stopped running it</label><br/>

                        <p>Commentary / useful information</p>
                        <textarea
                            type="text"
                            rows="15
                            cols="10"
                            wrap="soft"
                            maxlength="250"
                            id="stockComments"
                            placeholder="Commentery or useful info"
                        ></textarea><br/>

                    </div>

                    <br/>

                    <button type="submit" id="createInvRecordButt">Create Record</button>

                </form>

            </div>

            <br/>
            <button id="cancelGoInvButt">Cancel</button>

        </div>
    `;

    const dropdownConfig = {
        stockType: stockClasses,
        stockWheelType: wheelClasses,
        stockCouplerType: couplerClasses,
        stockPower: powerClasses
    };

    populateDropdownsFromConfig(container, dropdownConfig);

    attachCancelListener("cancelGoInvButt", container);

}

function populateDropdownsFromConfig(container, config, placeholder = "Please select") {
    Object.entries(config).forEach(([selectId, options]) => {

        const selectElement = container.querySelector(`#${selectId}`);
        if (!selectElement) {
            console.warn(`Dropdown with ID #${selectId} not found in container`);
            return;
        }

        // INSTALL PLACEHOLDER
        const defaultOpt = document.createElement("option");
        defaultOpt.disabled = true;
        defaultOpt.selected = true;
        defaultOpt.textContent = placeholder;
        selectElement.appendChild(defaultOpt);

        // INSTALL OPTIONS
        options.forEach(option => {
            const opt = document.createElement("option");
            opt.value = option;
            opt.textContent = option;
            selectElement.appendChild(opt);
        });

    });
}

async function generateInvRecord(event) {
    event.preventDefault();
    
    const container = document.querySelector('.inventoryContainer');
    const ownerId = container.dataset.invOwner;
    
    //REQUIRED FIELDS
    const payload = {
        clientId: document.getElementById("clientId").value,
        stockType: document.getElementById("stockType").value,
        stockName: document.getElementById("stockName").value.trim(),
        ownerId
    }

    //OPTIONAL FIELDS
    const optionalFields = [
        "stockRoadNumber", "stockRailroad", "stockLivery", "stockPower",
        "purchaseCost", "purchaseDate", "stockWheelType", "stockBrand",
        "stockCouplerType", "stockComments", "prototypeStart","prototypeEnd"
    ];

    optionalFields.forEach((fieldId) => {
        const value = document.getElementById(fieldId).value.trim();
        if (value !== "") {
            payload[fieldId] = value;
        }
    });

    // const stockRoadNumber = document.getElementById("stockRoadNumber").value.trim();
    // const stockRailroad = document.getElementById("stockRailroad").value.trim();
    // const stockLivery = document.getElementById("stockLivery").value.trim();
    // const stockPower = document.getElementById("stockPower").value;
    // const purchaseCost = document.getElementById("purchaseCost").value;
    // const purchaseDate = document.getElementById("purchaseDate").value;
    // const stockWheelType = document.getElementById("stockWheelType").value;
    // const stockCouplerType = document.getElementById("stockCouplerType").value;
    // const stockComments = document.getElementById("stockComments").value.trim();
    // const prototypeStart = document.getElementById("prototypeStart").value;
    // const prototypeEnd = document.getElementById("prototypeEnd").value;

    try {
        const response = await fetch(apiUrl("/inventory"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
            },
            body: JSON.stringify(payload)
        });

    if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Record creation failed");
        }

        alert("Record was created successfully.");
        window.location.href = "/inventory";
    } catch (error) {
        alert("Error: " + error.message);
    }
}