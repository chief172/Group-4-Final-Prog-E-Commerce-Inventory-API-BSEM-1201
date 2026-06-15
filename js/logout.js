/**
 * Logout Functionality
 * Handles user logout across all pages
 */

document.addEventListener("DOMContentLoaded", function() {
    // Find all logout buttons and attach event listeners
    const logoutButtons = document.querySelectorAll("#logoutBtn, .logout-btn, [data-logout]");
    
    logoutButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            logoutUser();
        });
    });
});

// Also handle logout from any dynamic content
document.body.addEventListener("click", function(e) {
    if (e.target.closest("#logoutBtn") || e.target.closest(".logout-btn") || e.target.closest("[data-logout]")) {
        e.preventDefault();
        logoutUser();
    }
});