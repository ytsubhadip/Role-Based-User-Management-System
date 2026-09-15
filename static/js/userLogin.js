const userLoginForm = document.getElementById("userLoginForm");
const loginStatus = document.getElementById("loginStatus");

userLoginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginStatus.textContent = "Signing in...";

    const email = document.getElementById("UserEmail").value;
    const password = document.getElementById("UserPassword").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Unable to sign in.");
        }

        loginStatus.textContent = result.message || "Login successful.";
    } catch (error) {
        loginStatus.textContent = error.message || "Unable to reach the server.";
    }
});

