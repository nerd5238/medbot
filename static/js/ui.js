// ui.js

// -------------------------------
// Smooth Fade-In on Page Load
// -------------------------------
document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("fade-in");
});


// -------------------------------
// Scroll-to-Top Button
// -------------------------------
const scrollBtn = document.getElementById("scrollTopBtn");

if (scrollBtn) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 250) {
            scrollBtn.style.display = "block";
        } else {
            scrollBtn.style.display = "none";
        }
    });

    scrollBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}


// -------------------------------
// Dashboard Sidebar Active Highlight
// -------------------------------
function setActiveSidebar() {
    const current = window.location.pathname;
    const links = document.querySelectorAll(".sidebar a");

    links.forEach(link => {
        if (link.href.includes(current)) {
            link.classList.add("active-link");
        }
    });
}

setActiveSidebar();


// -------------------------------
// Toggle Password Visibility (Login + Signup)
// -------------------------------
const togglePassword = document.querySelectorAll(".toggle-password");

togglePassword.forEach(icon => {
    icon.addEventListener("click", () => {
        let input = icon.previousElementSibling;

        if (input.type === "password") {
            input.type = "text";
            icon.innerText = "🙈";
        } else {
            input.type = "password";
            icon.innerText = "👁️";
        }
    });
});
