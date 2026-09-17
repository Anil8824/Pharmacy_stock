const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        const message = document.getElementById("registerMessage");

        try {
            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Registration successful! Redirecting to login...";

                setTimeout(() => {
                    window.location.href = "/login";
                }, 1000);
            } else {
                message.textContent = data.error || "Registration failed.";
            }
        } catch (error) {
            message.textContent = "Unable to connect to the server.";
        }
    });
}

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document.getElementById("loginEmail").value.trim();
        const password = document.getElementById("loginPassword").value;

        const message = document.getElementById("loginMessage");

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Login successful! Redirecting...";

                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
            } else {
                message.textContent = data.error || "Login failed.";
            }
        } catch (error) {
            message.textContent = "Unable to connect to the server.";
        }
    });
}

let currentPage = 1;
let currentSearch = "";
let currentSortBy = "name";
let currentSortOrder = "asc";


async function loadMedicines(
    search = currentSearch,
    page = currentPage
) {
    const medicineList =
        document.getElementById("medicineList");

    if (!medicineList) {
        return;
    }

    currentSearch = search;
    currentPage = page;

    medicineList.innerHTML =
        "<p>Loading medicines...</p>";

    try {
        const response = await fetch(
            `/api/medicines?search=${encodeURIComponent(currentSearch)}` +
            `&page=${currentPage}` +
            `&limit=10` +
            `&sort_by=${currentSortBy}` +
            `&sort_order=${currentSortOrder}`
        );

        const data = await response.json();

        if (!response.ok) {
            medicineList.innerHTML =
                `<p>${data.error || "Failed to load medicines."}</p>`;
            return;
        }

        if (data.medicines.length === 0) {
            medicineList.innerHTML =
                "<p>No medicines found.</p>";
        } else {
            medicineList.innerHTML =
                data.medicines.map(medicine => `
                    <div class="medicine-card">
                        <h3>${medicine.name}</h3>

                        <p>
                            Generic:
                            ${medicine.generic_name || "Not specified"}
                        </p>

                        <button
                            class="primary-button"
                            onclick="viewStock(${medicine.id})">
                            View Stock
                        </button>
                    </div>
                `).join("");
        }

        const pageInfo =
            document.getElementById("pageInfo");

        if (pageInfo) {
            pageInfo.textContent =
                `Page ${data.pagination.page}`;
        }

        const previousPage =
            document.getElementById("previousPage");

        const nextPage =
            document.getElementById("nextPage");

        if (previousPage) {
            previousPage.disabled =
                data.pagination.page <= 1;
        }

        if (nextPage) {
            nextPage.disabled =
                data.pagination.page >=
                data.pagination.total_pages;
        }

    } catch (error) {
        medicineList.innerHTML =
            "<p>Unable to connect to the server.</p>";
    }
}


async function viewStock(medicineId) {
    try {
        const response = await fetch(
            `/api/medicines/${medicineId}/stock`
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Unable to fetch stock.");
            return;
        }

        alert(
           `${data.medicine || "Medicine"}\n\n` +
            `Sellable Stock: ${data.sellable_stock}\n` +
            `As of: ${data.as_of_date}`
        );

    } catch (error) {
        alert("Unable to connect to the server.");
    }
}


const searchButton = document.getElementById("searchButton");

if (searchButton) {
    searchButton.addEventListener("click", function () {
        const search = document
            .getElementById("medicineSearch")
            .value
            .trim();

        loadMedicines(search);
    });
}


if (document.getElementById("medicineList")) {
    loadMedicines();
}

async function loadExpiryAlerts() {
    const alertsContainer = document.getElementById("expiryAlerts");

    if (!alertsContainer) {
        return;
    }

    try {
        const response = await fetch("/api/alerts/expiring?days=30");
        const data = await response.json();

        if (!response.ok) {
            alertsContainer.innerHTML =
                `<p>${data.error || "Failed to load expiry alerts."}</p>`;
            return;
        }

        if (data.alerts.length === 0) {
            alertsContainer.innerHTML =
                "<p>No batches are expiring within the next 30 days.</p>";
            return;
        }

        alertsContainer.innerHTML = data.alerts.map(alert => `
            <div class="alert-card">
                <strong>${alert.medicine_name}</strong>
                <p>Batch: ${alert.batch_number}</p>
                <p>Quantity: ${alert.quantity}</p>
                <p>Expiry Date: ${alert.expiry_date}</p>
            </div>
        `).join("");

    } catch (error) {
        alertsContainer.innerHTML =
            "<p>Unable to connect to the server.</p>";
    }
}


if (document.getElementById("expiryAlerts")) {
    loadExpiryAlerts();
}

const medicineForm = document.getElementById("medicineForm");

if (medicineForm) {
    medicineForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const name = document.getElementById("medicineName").value.trim();
        const genericName = document.getElementById("genericName").value.trim();
        const message = document.getElementById("medicineMessage");

        try {
            const response = await fetch("/api/medicines", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    generic_name: genericName
                })
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Medicine added successfully!";
                medicineForm.reset();

                loadMedicines();
            } else {
                message.textContent =
                    data.error || "Failed to add medicine.";
            }

        } catch (error) {
            message.textContent =
                "Unable to connect to the server.";
        }
    });
}

const batchForm = document.getElementById("batchForm");

if (batchForm) {
    batchForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const medicineId =
            document.getElementById("batchMedicineId").value;

        const batchNumber =
            document.getElementById("batchNumber").value.trim();

        const quantity =
            document.getElementById("batchQuantity").value;

        const expiryDate =
            document.getElementById("expiryDate").value;

        const message =
            document.getElementById("batchMessage");

        try {
            const response = await fetch(
                `/api/medicines/${medicineId}/batches`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        batch_number: batchNumber,
                        quantity: Number(quantity),
                        expiry_date: expiryDate
                    })
                }
            );

            const data = await response.json();

            if (response.ok) {
                message.textContent =
                    "Batch added successfully!";

                batchForm.reset();

                loadMedicines();
            } else {
                message.textContent =
                    data.error || "Failed to add batch.";
            }

        } catch (error) {
            message.textContent =
                "Unable to connect to the server.";
        }
    });
}

const dispenseForm = document.getElementById("dispenseForm");

if (dispenseForm) {
    dispenseForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const medicineId =
            document.getElementById("dispenseMedicineId").value;

        const quantity =
            document.getElementById("dispenseQuantity").value;

        const message =
            document.getElementById("dispenseMessage");

        try {
            const response = await fetch(
                `/api/medicines/${medicineId}/dispense`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        quantity: Number(quantity)
                    })
                }
            );

            const data = await response.json();

            if (response.ok) {
                const batches = data.dispensed_batches
                    .map(batch =>
                        `${batch.batch_number}: ${batch.quantity}`
                    )
                    .join(", ");

                message.textContent =
                    `Dispensed successfully. Batches used: ${batches}`;

                dispenseForm.reset();

                loadMedicines();
                loadExpiryAlerts();

            } else {
                message.textContent =
                    data.error || "Unable to dispense medicine.";
            }

        } catch (error) {
            message.textContent =
                "Unable to connect to the server.";
        }
    });
}

const sortBySelect = document.getElementById("sortBy");

const sortOrderSelect =
    document.getElementById("sortOrder");

const previousPage =
    document.getElementById("previousPage");

const nextPage =
    document.getElementById("nextPage");


if (sortBySelect) {
    sortBySelect.addEventListener("change", function () {
        currentSortBy = this.value;

        loadMedicines(currentSearch, 1);
    });
}


if (sortOrderSelect) {
    sortOrderSelect.addEventListener("change", function () {
        currentSortOrder = this.value;

        loadMedicines(currentSearch, 1);
    });
}


if (previousPage) {
    previousPage.addEventListener("click", function () {
        if (currentPage > 1) {
            loadMedicines(
                currentSearch,
                currentPage - 1
            );
        }
    });
}


if (nextPage) {
    nextPage.addEventListener("click", function () {
        loadMedicines(
            currentSearch,
            currentPage + 1
        );
    });
}