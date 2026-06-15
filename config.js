/**
 * API Configuration
 * Centralized configuration for API endpoints and settings
 */

// API Base URL - Change this to your backend URL
const API_BASE_URL = "http://localhost:8000";

// API Endpoints
const API_ENDPOINTS = {
    // ========== AUTHENTICATION ==========
    LOGIN: `${API_BASE_URL}/auth/login`,
    REGISTER: `${API_BASE_URL}/auth/register`,
    GET_ME: `${API_BASE_URL}/auth/me`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
    
    // ========== USERS (Admin only) ==========
    USERS: `${API_BASE_URL}/admin/users`,
    USER: (id) => `${API_BASE_URL}/admin/users/${id}`,
    MAKE_ADMIN: (id) => `${API_BASE_URL}/admin/users/${id}/make-admin`,
    REMOVE_ADMIN: (id) => `${API_BAME_URL}/admin/users/${id}/remove-admin`,
    ACTIVATE_USER: (id) => `${API_BASE_URL}/admin/users/${id}/activate`,
    DEACTIVATE_USER: (id) => `${API_BASE_URL}/admin/users/${id}/deactivate`,
    
    // ========== CATEGORIES ==========
    CATEGORIES: `${API_BASE_URL}/categories`,
    CATEGORY: (id) => `${API_BASE_URL}/categories/${id}`,
    ADMIN_CATEGORIES: `${API_BASE_URL}/admin/categories`,
    ADMIN_CATEGORY: (id) => `${API_BASE_URL}/admin/categories/${id}`,
    
    // ========== PRODUCTS ==========
    PRODUCTS: `${API_BASE_URL}/products`,
    PRODUCT: (id) => `${API_BASE_URL}/products/${id}`,
    LOW_STOCK: `${API_BASE_URL}/products/low-stock`,
    ADMIN_PRODUCTS: `${API_BASE_URL}/admin/products`,
    ADMIN_PRODUCT: (id) => `${API_BASE_URL}/admin/products/${id}`,
    BULK_STOCK_UPDATE: `${API_BASE_URL}/admin/products/bulk-stock-update`,
    
    // ========== CART ==========
    CART: (userId) => `${API_BASE_URL}/cart/${userId}`,
    ADD_TO_CART: `${API_BASE_URL}/cart`,
    UPDATE_CART_ITEM: (itemId) => `${API_BASE_URL}/cart/${itemId}`,
    REMOVE_CART_ITEM: (itemId) => `${API_BASE_URL}/cart/${itemId}`,
    CLEAR_CART: (userId) => `${API_BASE_URL}/cart/clear/${userId}`,
    
    // ========== ORDERS ==========
    ORDERS: `${API_BASE_URL}/orders`,
    ORDER: (id) => `${API_BASE_URL}/orders/${id}`,
    USER_ORDERS: (userId) => `${API_BASE_URL}/orders/user/${userId}`,
    ADMIN_ORDERS: `${API_BASE_URL}/admin/orders`,
    ADMIN_ORDER: (id) => `${API_BASE_URL}/admin/orders/${id}`,
    UPDATE_ORDER_STATUS: (id, status) => `${API_BASE_URL}/admin/orders/${id}/status?status_value=${status}`,
    CANCEL_ORDER: (id) => `${API_BASE_URL}/admin/orders/${id}/cancel`,
    
    // ========== DASHBOARD (Admin only) ==========
    DASHBOARD_STATS: `${API_BASE_URL}/admin/dashboard/stats`,
    TOP_PRODUCTS: `${API_BASE_URL}/admin/dashboard/top-products`,
    SALES_BY_CATEGORY: `${API_BASE_URL}/admin/dashboard/sales-by-category`,
    DAILY_SALES: `${API_BASE_URL}/admin/dashboard/daily-sales`,
    REVENUE_SUMMARY: `${API_BASE_URL}/admin/dashboard/revenue-summary`,
    
    // ========== SYSTEM ==========
    SYSTEM_INFO: `${API_BASE_URL}/admin/system/info`,
    HEALTH_CHECK: `${API_BASE_URL}/health`,
    SEED_DEMO_DATA: `${API_BASE_URL}/admin/system/seed-demo-data`,
};

// Helper function for API calls
async function apiCall(url, method = "GET", data = null, requiresAuth = true) {
    const headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    };
    
    if (requiresAuth) {
        const token = localStorage.getItem("access_token");
        if (!token) {
            if (requiresAuth) {
                window.location.href = "/login.html";
                throw new Error("No authentication token found");
            }
        } else {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }
    
    const config = {
        method,
        headers,
    };
    
    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, config);
        
        // Handle 401 Unauthorized
        if (response.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            if (requiresAuth && !window.location.pathname.includes("login")) {
                window.location.href = "/login.html";
            }
            throw new Error("Session expired. Please login again.");
        }
        
        return response;
    } catch (error) {
        console.error("API call error:", error);
        throw error;
    }
}

// Get current user from localStorage
function getCurrentUser() {
    const userStr = localStorage.getItem("user");
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

// Get auth token
function getAuthToken() {
    return localStorage.getItem("access_token");
}

// Check if user is admin
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === "admin";
}

// Check if user is authenticated
function isAuthenticated() {
    return !!localStorage.getItem("access_token");
}

// Check if user is customer
function isCustomer() {
    const user = getCurrentUser();
    return user && user.role === "customer";
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = "/login.html";
        return false;
    }
    return true;
}

// Redirect to dashboard if already authenticated
function requireGuest() {
    if (isAuthenticated()) {
        const user = getCurrentUser();
        if (user?.role === "admin") {
            window.location.href = "/dashboard.html";
        } else {
            window.location.href = "/products.html";
        }
        return false;
    }
    return true;
}

// Redirect if not admin
function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
        window.location.href = "/products.html";
        return false;
    }
    return true;
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show message
function showMessage(message, type = "info") {
    const messageDiv = document.getElementById("message") || createMessageDiv();
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = "block";
    
    setTimeout(() => {
        messageDiv.style.display = "none";
    }, 3000);
}

function createMessageDiv() {
    const div = document.createElement("div");
    div.id = "message";
    document.body.insertBefore(div, document.body.firstChild);
    return div;
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}