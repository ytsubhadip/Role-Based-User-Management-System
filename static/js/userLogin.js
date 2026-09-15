const userLoginForm = document.getElementById("userLoginForm");

userLoginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

    const email = document.getElementById("UserEmail").value;
    const password = document.getElementById("UserPassword").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
        const data = await response.json();
        alert("Login successful!");
    }
        
    if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.detail);
    }
});

