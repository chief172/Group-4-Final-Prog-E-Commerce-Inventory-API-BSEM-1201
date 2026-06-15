/**
 * Authentication Functions
 * Handles user registration, login, and session management
 */

// Register new user
async function registerUser(username, email, password, role = "customer") {
    try {
        const response = await fetch(API_ENDPOINTS.REGISTER, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username,
                email,
                password,
                role
            }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Registration successful! Welcome ${username}!`, "success");
            setTimeout(() => {
                window.location.href = "/login.html";
            }, 1500);
            return data;
        } else {
            showMessage(data.detail || "Registration failed. Please try again.", "error");
            return null;
        }
    } catch (error) {
        console.error("Registration error:", error);
        showMessage("Network error. Please check your connection.", "error");
        return null;
    }
}

// Login user
async function loginUser(email, password) {
    try {
        const response = await fetch(API_ENDPOINTS.LOGIN, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and user data
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("user", JSON.stringify(data.user));
            
            showMessage(`Welcome back, ${data.user.username}!`, "success");
            
            // Redirect based on role
            setTimeout(() => {
                if (data.user.role === "admin") {
                    window.location.href = "/dashboard.html";
                } else {
                    window.location.href = "/products.html";
                }
            }, 1000);
            return data;
        } else {
            showMessage(data.detail || "Invalid email or password", "error");
            return null;
        }
    } catch (error) {
        console.error("Login error:", error);
        showMessage("Network error. Please check your connection.", "error");
        return null;
    }
}

// Logout user
function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    showMessage("Logged out successfully!", "success");
    setTimeout(() => {
        window.location.href = "/login.html";
    }, 500);
}

// Get current user info from API
async function fetchCurrentUser() {
    if (!isAuthenticated()) return null;
    
    try {
        const response = await apiCall(API_ENDPOINTS.GET_ME, "GET", null, true);
        if (response.ok) {
            const user = await response.json();
            localStorage.setItem("user", JSON.stringify(user));
            return user;
        }
    } catch (error) {
        console.error("Error fetching user:", error);
    }
    return null;
}

// Update user profile
async function updateUserProfile(userId, userData) {
    try {
        const response = await apiCall(API_ENDPOINTS.USER(userId), "PUT", userData, true);
        if (response.ok) {
            const user = await response.json();
            if (user.id === getCurrentUser()?.id) {
                localStorage.setItem("user", JSON.stringify(user));
            }
            showMessage("Profile updated successfully!", "success");
            return user;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to update profile", "error");
            return null;
        }
    } catch (error) {
        console.error("Error updating profile:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Change password
async function changePassword(oldPassword, newPassword) {
    // This would need a dedicated endpoint
    // For now, just show a message
    showMessage("Password change feature coming soon!", "info");
}

// Display user info in navbar
function displayUserInfo() {
    const user = getCurrentUser();
    const userInfoDiv = document.getElementById("userInfo");
    
    if (userInfoDiv && user) {
        userInfoDiv.innerHTML = `
            <span class="user-name">${escapeHtml(user.username)}</span>
            <span class="user-role badge ${user.role}">${user.role}</span>
        `;
    }
}

// Initialize auth checks on page load
document.addEventListener("DOMContentLoaded", function() {
    displayUserInfo();
    
    // Setup logout button if exists
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function(e) {
            e.preventDefault();
            logoutUser();
        });
    }
});