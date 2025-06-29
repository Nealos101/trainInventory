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
            console.log("Admin functions have not been created for this page yet.")
            // const script = document.createElement("script");
            // script.src = "/static/js/inventoryAdmin.js";
            // script.type = "module"
            // document.head.appendChild(script);
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
        const invResponse = await authFetch(apiUrl(`/inventory/${invOwner}`), {
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
        // console.log(invData);

        return loadedInventoryLanding(
            container, invData, invOwner
        );

    } catch (error) {
        console.log("Error loading inventory: " + error.message);
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

    attachCreateEditRecordListener("createNewRecordButt", container);

    const viewButtons = container.querySelectorAll(".viewBtn");

    viewButtons.forEach(button => {
        button.addEventListener("click", async () => {
            const invId = button.dataset.id;

            try {

                const response = await authFetch(apiUrl(`/inventory/${invOwner}/${invId}`), {
                    headers: {
                        "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                    }
                 });

                if (!response.ok) {
                    throw new Error("Failed to load record");
                }

                const invDetails = await response.json();

                // LOAD THE PAGE
                return inventoryRecordPage(container, invDetails, invOwner, invId);

            } catch (error) {
                console.error("Record load failed, info: ", error.message);
            }
        });
    });
}

// 

function inventoryRecordPage(container, invDetails, invOwner, invId) {
    
    container.innerHTML =`
        <div class="inventoryContainer" data-inv-owner="${invOwner}">

            <button id="editInvButt">Edit this record</button>

            <h2>About ${invDetails.clientId}, a ${invDetails.stockName}</h2>

            <div class="invAddOptional">

                <h3>Main Identifiers</h3>

                <table class="inventoryTable">
                    <tr>
                        <th>Your Stock Id</th>
                        <td>${invDetails.clientId}</td>
                    </tr>
                    <tr>
                        <th>Stock Name</th>
                        <td>${invDetails.stockName}</td>
                    </tr>
                    <tr>
                        <th>Road Number</th>
                        <td>${invDetails.stockRoadNumber}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>${invDetails.stockType}</td>
                    </tr>
                </table>

            </div>

            <div class="invAddOptional">

                <h3>Additional Details</h3>

                <h4>Supporting Information</h4>

                <table class="inventoryTable">
                    <tr>
                        <th>Brand</th>
                        <td>${invDetails.stockBrand}</td>
                    </tr>
                    <tr>
                        <th>Railroad</th>
                        <td>${invDetails.stockRailroad}</td>
                    </tr>
                   <tr>
                        <th>Livery</th>
                        <td>${invDetails.stockLivery}</td>
                    </tr>
                   <tr>
                        <th>Purchase Price</th>
                        <td>£${invDetails.purchaseCost}</td>
                    </tr>
                    <tr>
                        <th>Purchase Date</th>
                        <td>${invDetails.purchaseDate}</td>
                    </tr>
                    <tr>
                        <th>Comments and Notes</th>
                        <td>${invDetails.stockComments}</td>
                    </tr>
                </table>

                <h4>Materials and Power</h4>

                <table class="inventoryTable">
                    <tr>
                        <th>Power</th>
                        <td>${invDetails.stockPower}</td>
                    </tr>
                    <tr>
                        <th>Wheels</th>
                        <td>${invDetails.stockWheelType}</td>
                    </tr>
                    <tr>
                        <th>Couplers</th>
                        <td>${invDetails.stockCouplerType}</td>
                    </tr>
                </table>

                <h4>Prototype tracking</h4>

                <table class="inventoryTable">
                    <tr>
                        <th>Prototype Start Date</th>
                        <td>${invDetails.prototypeStart}</td>
                    </tr>
                    <tr>
                        <th>Prototype Removal Date</th>
                        <td>${invDetails.prototypeEnd}</td>
                    </tr>
                </table>

            </div>

            <br/>

            <button id="cancelGoInvButt">Cancel</button>

        </div>
    `;

    attachCreateEditRecordListener("editInvButt", container, invDetails, invId)

    attachCancelListener("cancelGoInvButt", container);

}


function unloadedInventoryLanding(container, invOwner) {

    container.innerHTML=`
        <div class="inventoryContainer" data-inv-owner="${invOwner}">
            <h2>No Inventory yet</h2>
            <p>It looks like you don't have any inventory on Trainweb yet. Ready to change that? Click the button below!</p>

                <button id="createNewRecordButt">Create a record</button>

        </div>
    `;

    attachCreateEditRecordListener("createNewRecordButt", container);

}

// BUTTON LISTENER FOR CREATE NEW RECORD
function attachCreateEditRecordListener(buttonId, container, record = null, invId = null) {
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

            fetchEnums(container, ownerId, record, invId);
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

async function fetchEnums(container, ownerId, record = null, invId = null) {
    // console.log("Enum pull was started");

    //CALLS THE ENDPOINT
    try {
        const response = await fetch(apiUrl(`/enum/`));
        if (!response.ok) {
            throw new Error("Failed to fetch enums");
        }

        //CAPTURE RETURNED ENUMS
        const enumData = await response.json();

        // console.log(enumData);
        const wheelClasses = enumData.wheelClasses;
        const couplerClasses = enumData.couplerClasses;
        const powerClasses = enumData.powerClasses;
        const stockClasses = enumData.stockClasses;

        return renderInventoryForm(
            container,
            ownerId,
            wheelClasses,
            couplerClasses,
            powerClasses,
            stockClasses,
            record,
            invId
        );

        } catch (error) {
            alert("Error loading enums, info: " + error.message);
            window.location.reload();
        }
}


function renderInventoryForm(
    container,
    invOwner,
    wheelClasses,
    couplerClasses,
    powerClasses,
    stockClasses,
    record = null, //IF = NULL, THIS WILL TRIGGER CREATE MODE
    invId = null
) {

    // MAIN DECISION POINT
    const isEdit = !!record;

    // THESE ARE ALL DISPLAYS BASED ON DECISION POINT
    const actionTitle = isEdit ? "Update an Inventory Record" : "Create an Inventory Record";
    const buttonText = isEdit ? "Update Record" : "Create Record";

    const isRequired = isEdit
        ? ""
        : "required";

    const titleDesc = isEdit
        ? "Use the form below to update this record. When done, click 'Update Record' to save any changes. Only filled fields will be recorded in our database."
        : "All data recorded in the below form will be recorded in our database.";

    const identDesc = isEdit
        ? "These are the Main Identifiers. Any new 'Your Stock Id' needs to be unique to your Inventory, and not the existing one."
        : "These fields need to be filled to create a record.";

    const optionalTitleDesc = isEdit
        ? "Additional Fields"
        : "Optional Fields" ;

    const optionalDesc = isEdit
        ? "These fields give information to support the identification of the model."
        : "These fields don't need to be filled in... Buy why wouldn't you?";

    function getInputAttr(fieldValue, placeholder) {
        return isEdit
            ? `${fieldValue || ''}`
            : `${placeholder};`
    } //HELPER FUNCTION TO WORK WITH PLACEHOLDERS IN THE EVENT THIS IS A CREATE

    container.innerHTML =`
        <div class="inventoryContainer" data-inv-owner="${invOwner}">
            <h2>${actionTitle}</h2>
            <p>${titleDesc} Although the admins of TrainWeb have made their best efforts to secure the site, nasty people will still try to hack in and steal the data.</p>
            <p>Therefore, the TrainWeb admins recommend you "spoof" any information you deem sensitive.</p>

            <div class="createRecordForm">
                <form id="invForm">

                    <h3>Required Fields</h3>
                    <p>These fields need to be filled to create a record.</p>

                    <div class="invAddRequired">

                        <p>${identDesc}</p>

                        <input
                            type="text"
                            id="clientId"
                            placeholder="${getInputAttr(record?.clientId, 'Your Stock Identifier')}"
                            ${isRequired}
                        >
                        <label for "clientId"> Must be unique to your Inventory</label><br/>

                        <input
                            type="text"
                            id="stockName"
                            placeholder="${getInputAttr(record?.stockName, 'Name')}"
                            ${isRequired}
                        >
                        <label for "stockName"> Usually make and model</label><br/>

                        <input
                            type="text"
                            id="stockRoadNumber"
                            placeholder="${getInputAttr(record?.stockRoadNumber, 'Road number')}"
                        >
                        <label for "stockRoadNumber"> Designation normally found on the sides</label><br/>

                        <p>Stock Type Selector</p>

                        <select id="stockType"></select>
                        <label for "stockType"> Select the type</label><br/>
                    
                    </div>

                    <h3>${optionalTitleDesc}</h3>
                    <p>${optionalDesc}</p>

                    <div class="invAddOptional">

                    <p>About the Item</p>
                    
                        <input
                            type="text"
                            id="stockBrand"
                            placeholder="${getInputAttr(record?.stockBrand, 'Manufacturer')}"
                        >
                        <label for "stockBrand"> Who made it</label><br/>

                        <input
                            type="text"
                            id="stockRailroad"
                            placeholder="${getInputAttr(record?.stockRailroad, 'Name of railroad')}"
                        >
                        <label for "stockRailroad"> Details of the owner or company found with the livery</label><br/>

                        <input
                            type="text"
                            id="stockLivery"
                            placeholder="${getInputAttr(record?.stockLivery, 'Livery')}"
                        >
                        <label for "stockLivery"> The scheme (or just use descriptors)</label><br/>

                        <input
                            type="decimal"
                            id="purchaseCost"
                            placeholder="${getInputAttr(record?.purchaseCost, '1234.00')}"
                        >
                        <label for "purchaseCost"> The cost, just as a number</label><br/>

                        <input
                            type="date"
                            id="purchaseDate"
                        >
                        <label for "purchaseDate"> The date you purchased</label>
                        <small><em>Current: ${record?.purchaseDate || 'Not set'}</small></em><br/>

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
                        >
                        <label for "prototypeStart"> The date the prototype introduced it</label>
                        <small><em>Current: ${record?.prototypeStart || 'Not set'}</small></em><br/>

                        <input
                            type="date"
                            id="prototypeEnd"
                        >
                        <label for "prototypeEnd"> The date when the prototype stopped running it</label>
                        <small><em>Current: ${record?.prototypeEnd || 'Not set'}</small></em><br/>

                        <p>Commentary / useful information</p>
                        <textarea
                            type="text"
                            rows="15
                            cols="10"
                            wrap="soft"
                            maxlength="250"
                            id="stockComments"
                            placeholder="${getInputAttr(record?.stockComments, 'Commentery or useful info')}"
                        ></textarea><br/>

                    </div>

                    <br/>

                    <button type="submit" id="${isEdit ? 'updateInvRecordButt' : 'createInvRecordButt'}">${buttonText}</button>

                </form>

            </div>

            <br/>
            <button id="cancelGoInvButt">Cancel</button>

        </div>
    `;

    // POPULATE DROPDOWNS
    const dropdownConfig = {
        stockType: stockClasses,
        stockWheelType: wheelClasses,
        stockCouplerType: couplerClasses,
        stockPower: powerClasses
    };

    populateDropdownsFromConfig(container, dropdownConfig, "Please select");

    if (isEdit) {
        if (record.stockType) container.querySelector("#stockType").value = record.stockType;
        if (record.stockWheelType) container.querySelector("#stockWheelType").value = record.stockWheelType;
        if (record.stockCouplerType) container.querySelector("#stockCouplerType").value = record.stockCouplerType;
        if (record.stockPower) container.querySelector("#stockPower").value = record.stockPower;
    }

    attachCancelListener("cancelGoInvButt", container);

    const form = container.querySelector("#invForm");
    if (form) {
        form.addEventListener("submit", (e) => generateUpdateInvRecord(e, invId, record))
    }

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

// REUSABLE FUNCTION TO ENSURE SELECT ELEMENTS DON'T HAVE THE PLACEHOLDER OR EXISTING DATA WHEN EDITING
function isMeaningfulSelect(element, fieldId, record = null) {

    if (element.tagName !== "SELECT") return true;

    const selectedOption = element.options[element.selectedIndex];

    // ALLOW IF IT IS NOT THE PLACEHOLDER
    if (!selectedOption.disabled) return true;

    // IF IN EDIT MODE AND RECORD EXISTS, AND THE RECORD HAS A VALUE
    if (record && record[fieldId]) return true;

    //OTHERWISE THIS IS JUST A PLACEHOLDER
    return false;
}

async function generateUpdateInvRecord(event, invId = null, record = null) {
    event.preventDefault();
    
    // console.log("generateUpdateInvRecord has started")

    const isEdit = !!invId;

    const container = document.querySelector('.inventoryContainer');
    const ownerId = container.dataset.invOwner;
    
    //INITIAL PAYLOAD (IF CREATE, POPULATES REQUIRED FIELDS)
    const payload = isEdit
        ? {}
        :{
            clientId: document.getElementById("clientId").value,
            stockType: document.getElementById("stockType").value,
            stockName: document.getElementById("stockName").value.trim(),
            stockRoadNumber: document.getElementById("stockRoadNumber").value.trim(),
            ownerId
        }

    //BUILD FIELDS
    const identFields = [
        "clientId", "stockType", "stockName", "stockRoadNumber"
    ]
    
    const optionalFields = [
        "stockRailroad", "stockLivery", "stockPower",
        "purchaseCost", "purchaseDate", "stockWheelType", "stockBrand",
        "stockCouplerType", "stockComments", "prototypeStart","prototypeEnd"
    ];

    // DEFINES THE ARRAY TO USE
    const allFields = isEdit
        ? [...identFields, ...optionalFields] // ARRAY WITH ALL FIELDS IF EDITING
        : optionalFields // ARRAY WITH OPTIONAL FIELDS IF CREATING

    // console.log("Starting loop")
    // console.log(allFields)

    allFields.forEach((fieldId) => {
        const element = document.getElementById(fieldId);
        if (!element) return;

        let value = element.value;

        if (element.type === "text" || element.tagName === "TEXTAREA") {
            value = value.trim();
        }

        const hasValue =
            value !== "" &&
            value !== null &&
            value !== undefined &&
            !(element.type === "number" && isNaN(parseFloat(value)));

        const shouldInclude = isMeaningfulSelect(element, fieldId, isEdit ? record : null) &&
            hasValue &&
            (!isEdit || value !== record?.[fieldId]);

        if (shouldInclude) {
            payload[fieldId] = value;
        }

    });

    const url = isEdit
        ? `/inventory/${ownerId}/${invId}`
        : "/inventory";
    const method = isEdit
        ? "PATCH"
        : "POST";
    const failMsg = isEdit
        ? "Record update failed"
        : "Record creation failed"
    const successMsg = isEdit
        ? `Record was updated successfully`
        : "Record was created successfully"

    // console.log(payload)

    try {
        const response = await authFetch(apiUrl(url), {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
            },
            body: JSON.stringify(payload)
        });

    if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || failMsg);
        }

        alert(successMsg);
        window.location.href = "/inventory";
    } catch (error) {
        alert("Error: " + error.message);
    }
}