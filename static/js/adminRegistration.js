const AdminRegistrationForm = document.getElementById("AdminRegistrationForm");
const adminRegistrationStatus = document.getElementById("adminRegistrationStatus");


AdminRegistrationForm.addEventListener("submit", async function (e) {
    e.preventDefault()
    adminRegistrationStatus.textContent = "Creating user...";

    const form_data = {
        role: document.getElementById("role").value,
        full_name: document.getElementById("userFullName").value,
        email: document.getElementById("UserEmail").value,
        standard: document.getElementById("Standerd").value,
        subject: document.getElementById("Subject").value
    }

    try {
        const response = await fetch("/admin/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(form_data)
        });
        const result = await response.json();

        if (!response.ok) {
            const detail = Array.isArray(result.detail)
                ? result.detail.map((item) => item.msg).join(" ")
                : result.detail;
            throw new Error(detail || "User creation failed.");
        }

        adminRegistrationStatus.textContent = result.message || "User created successfully.";
        AdminRegistrationForm.reset();
    } catch (error) {
        adminRegistrationStatus.textContent = error.message || "Unable to reach the server.";
    }
})
