const userLoginForm = document.getElementById("userLoginForm");

if (userLoginForm) {
    userLoginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("UserEmail").value;
        const password = document.getElementById("UserPassword").value;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Login failed");
                return;
            }

            if (data.status === "temporary_password") {
                window.location.href = `/verify-otp?user_id=${encodeURIComponent(data.user_id)}&email=${encodeURIComponent(data.email || email)}`;
                return;
            }

            if (data.role === "admin") window.location.href = "/admin/dashboard";
            else if (data.role === "teacher") window.location.href = "/teacher/dashboard";
            else if (data.role === "student") window.location.href = "/student/dashboard";
            else window.location.href = "/";

        } catch (err) {
            alert("Unable to reach the server.");
        }
    });
}
