/**
 * Admin Dashboard Functions
 * Handles dashboard statistics and analytics
 */

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await apiCall(API_ENDPOINTS.DASHBOARD_STATS, "GET", null, true);
        if (response.ok) {
            const stats = await response.json();
            displayStats(stats);
            return stats;
        } else {
            console.error("Failed to load dashboard stats");
            return null;
        }
    } catch (error) {
        console.error("Error loading dashboard stats:", error);
        return null;
    }
}

// Display statistics
function displayStats(stats) {
    // User stats
    document.getElementById("totalUsers")?.textContent = stats.users?.total || 0;
    document.getElementById("activeUsers")?.textContent = stats.users?.active || 0;
    document.getElementById("admins")?.textContent = stats.users?.admins || 0;
    document.getElementById("customers")?.textContent = stats.users?.customers || 0;
    document.getElementById("newUsers7d")?.textContent = stats.users?.new_last_7d || 0;
    
    // Product stats
    document.getElementById("totalProducts")?.textContent = stats.products?.total || 0;
    document.getElementById("activeProducts")?.textContent = stats.products?.active || 0;
    document.getElementById("lowStock")?.textContent = stats.products?.low_stock || 0;
    document.getElementById("outOfStock")?.textContent = stats.products?.out_of_stock || 0;
    document.getElementById("inventoryValue")?.textContent = formatCurrency(stats.products?.total_inventory_value || 0);
    
    // Order stats
    document.getElementById("totalOrders")?.textContent = stats.orders?.total || 0;
    document.getElementById("newOrders7d")?.textContent = stats.orders?.new_last_7d || 0;
    
    // Revenue stats
    document.getElementById("totalRevenue")?.textContent = formatCurrency(stats.revenue?.total || 0);
    document.getElementById("revenue7d")?.textContent = formatCurrency(stats.revenue?.last_7_days || 0);
}

// Load top products
async function loadTopProducts(limit = 10) {
    const container = document.getElementById("topProductsList");
    if (!container) return;
    
    container.innerHTML = '<tr><td colspan="4" class="text-center">Loading...</td></tr>';
    
    try {
        const response = await apiCall(`${API_ENDPOINTS.TOP_PRODUCTS}?limit=${limit}`, "GET", null, true);
        if (response.ok) {
            const products = await response.json();
            displayTopProducts(products);
            return products;
        }
    } catch (error) {
        console.error("Error loading top products:", error);
        container.innerHTML = '<tr><td colspan="4" class="text-center error">Failed to load</td></tr>';
    }
    return [];
}

// Display top products
function displayTopProducts(products) {
    const container = document.getElementById("topProductsList");
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<tr><td colspan="4">No sales data available</td></tr>';
        return;
    }
    
    let html = '';
    for (const product of products) {
        html += `
            <tr>
                <td>${escapeHtml(product.name)}</td>
                <td>${formatCurrency(product.price)}</td>
                <td>${product.total_sold}</td>
                <td>${formatCurrency(product.total_revenue)}</td>
            </tr>
        `;
    }
    container.innerHTML = html;
}

// Load daily sales
async function loadDailySales(days = 7) {
    const container = document.getElementById("dailySalesList");
    if (!container) return;
    
    container.innerHTML = '<tr><td colspan="3" class="text-center">Loading...</td></tr>';
    
    try {
        const response = await apiCall(`${API_ENDPOINTS.DAILY_SALES}?days=${days}`, "GET", null, true);
        if (response.ok) {
            const sales = await response.json();
            displayDailySales(sales);
            return sales;
        }
    } catch (error) {
        console.error("Error loading daily sales:", error);
        container.innerHTML = '<tr><td colspan="3" class="text-center error">Failed to load</td></tr>';
    }
    return [];
}

// Display daily sales
function displayDailySales(sales) {
    const container = document.getElementById("dailySalesList");
    if (!container) return;
    
    if (!sales || sales.length === 0) {
        container.innerHTML = '<tr><td colspan="3">No sales data available</td></tr>';
        return;
    }
    
    let html = '';
    for (const day of sales) {
        html += `
            <tr>
                <td>${day.date}</td>
                <td>${day.order_count}</td>
                <td>${formatCurrency(day.total_sales)}</td>
            </tr>
        `;
    }
    container.innerHTML = html;
}

// Load sales by category
async function loadSalesByCategory() {
    const container = document.getElementById("salesByCategory");
    if (!container) return;
    
    container.innerHTML = '<tr><td colspan="3" class="text-center">Loading...</td></tr>';
    
    try {
        const response = await apiCall(API_ENDPOINTS.SALES_BY_CATEGORY, "GET", null, true);
        if (response.ok) {
            const categories = await response.json();
            displaySalesByCategory(categories);
            return categories;
        }
    } catch (error) {
        console.error("Error loading sales by category:", error);
        container.innerHTML = '<tr><td colspan="3" class="text-center error">Failed to load</td></tr>';
    }
    return [];
}

// Display sales by category
function displaySalesByCategory(categories) {
    const container = document.getElementById("salesByCategory");
    if (!container) return;
    
    if (!categories || categories.length === 0) {
        container.innerHTML = '<tr><td colspan="3">No category sales data available</td></tr>';
        return;
    }
    
    let html = '';
    for (const category of categories) {
        html += `
            <tr>
                <td>${escapeHtml(category.name)}</td>
                <td>${category.total_sold}</td>
                <td>${formatCurrency(category.total_revenue)}</td>
            </tr>
        `;
    }
    container.innerHTML = html;
}

// Load revenue summary
async function loadRevenueSummary() {
    try {
        const response = await apiCall(API_ENDPOINTS.REVENUE_SUMMARY, "GET", null, true);
        if (response.ok) {
            const revenue = await response.json();
            displayRevenueSummary(revenue);
            return revenue;
        }
    } catch (error) {
        console.error("Error loading revenue summary:", error);
    }
    return null;
}

// Display revenue summary
function displayRevenueSummary(revenue) {
    if (!revenue) return;
    
    document.getElementById("revenueToday")?.textContent = formatCurrency(revenue.today || 0);
    document.getElementById("revenueThisWeek")?.textContent = formatCurrency(revenue.this_week || 0);
    document.getElementById("revenueThisMonth")?.textContent = formatCurrency(revenue.this_month || 0);
    document.getElementById("revenueThisYear")?.textContent = formatCurrency(revenue.this_year || 0);
    document.getElementById("revenueAllTime")?.textContent = formatCurrency(revenue.all_time || 0);
}

// Initialize dashboard
async function initDashboard() {
    if (!requireAdmin()) return;
    
    await loadDashboardStats();
    await loadTopProducts();
    await loadDailySales();
    await loadSalesByCategory();
    await loadRevenueSummary();
    
    // Auto-refresh every 30 seconds
    setInterval(async () => {
        await loadDashboardStats();
        await loadTopProducts();
        await loadDailySales();
    }, 30000);
}

// Auto-initialize if on dashboard page
if (document.getElementById("dashboard")) {
    document.addEventListener("DOMContentLoaded", initDashboard);
}