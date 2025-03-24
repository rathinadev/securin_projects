const API_URL = "http://127.0.0.1:8080"; // FastAPI Backend URL

let currentPage = 1;

// Function to Fetch CVEs
async function fetchCVEs(filters = {}) {
    let queryParams = new URLSearchParams({
        page: currentPage,
        results_per_page: 10
    });

    // Add filters if provided
    for (let key in filters) {
        if (filters[key]) {
            queryParams.append(key, filters[key]);
        }
    }

    try {
        const response = await fetch(`${API_URL}/cves?${queryParams.toString()}`);
        const data = await response.json();

        updateTable(data.data);
        document.getElementById("pageNumber").innerText = `Page ${currentPage}`;
    } catch (error) {
        console.error("Error fetching CVE data:", error);
    }
}

// Function to Update Table with CVE Data
function updateTable(cveData) {
    const tableBody = document.getElementById("cveTableBody");
    tableBody.innerHTML = ""; // Clear previous data

    cveData.forEach(cve => {
        let row = `<tr>
            <td>${cve.id}</td>
            <td>${cve.descriptions ? cve.descriptions[0].value : "N/A"}</td>
            <td>${cve.published}</td>
            <td>${cve.lastModified}</td>
            <td>${cve.metrics?.cvssMetricV2?.cvssData?.baseScore || "N/A"}</td>
        </tr>`;
        tableBody.innerHTML += row;
    });
}

// Function to Sync Data
document.getElementById("syncBtn").addEventListener("click", async () => {
    document.getElementById("syncStatus").innerText = "Syncing data...";
    
    try {
        const response = await fetch(`${API_URL}/sync`);
        const data = await response.json();
        document.getElementById("syncStatus").innerText = data.message;
    } catch (error) {
        document.getElementById("syncStatus").innerText = "Error syncing data.";
    }
});

// Function to Apply Filters
document.getElementById("filterBtn").addEventListener("click", () => {
    const filters = {
        cve_id: document.getElementById("cveId").value,
        year: document.getElementById("year").value,
        min_score: document.getElementById("minScore").value,
        last_modified_days: document.getElementById("lastModifiedDays").value
    };

    fetchCVEs(filters);
});

// Pagination Buttons
document.getElementById("prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        fetchCVEs();
    }
});

document.getElementById("nextPage").addEventListener("click", () => {
    currentPage++;
    fetchCVEs();
});

// Load Initial CVE Data
fetchCVEs();
