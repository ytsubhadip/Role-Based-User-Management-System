const RegistrationForm = document.getElementById("RegistrationForm");
const registrationStatus = document.getElementById("registrationStatus");

RegistrationForm.addEventListener( "submit", async(e)=>{
    e.preventDefault();
    registrationStatus.textContent = "Registering...";
    
    const form_data = {
        full_name : document.getElementById("userFullName").value,
        email : document.getElementById("UserEmail").value,
        password : document.getElementById("userPassowrd").value,
        role : document.getElementById("role").value,
        standard : document.getElementById("standard").value,
        subject : document.getElementById("Subject").value
    }

    try {
        const response = await fetch("/registration", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(form_data)
        });
        const result = await response.json();

        if (!response.ok) {
            const detail = Array.isArray(result.detail)
                ? result.detail.map((item) => item.msg).join(" ")
                : result.detail;
            throw new Error(detail || "Registration failed.");
        }

        registrationStatus.textContent = result.message || "Registration successful.";
        RegistrationForm.reset();
    } catch (error) {
        registrationStatus.textContent = error.message || "Unable to reach the server.";
    }
})