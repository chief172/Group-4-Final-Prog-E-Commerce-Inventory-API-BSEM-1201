/**
 * Category Management Functions
 * Handles category listing, creation, editing, deletion
 */

// Load all categories
async function loadCategories(containerId, adminMode = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading categories...</p></div>';
    
    try {
        const url = adminMode ? API_ENDPOINTS.ADMIN_CATEGORIES : API_ENDPOINTS.CATEGORIES;
        const response = await fetch(url);
        
        if (response.ok) {
            const categories = await response.json();
            displayCategories(categories, container, adminMode);
            return categories;
        } else {
            container.innerHTML = '<p class="error">Failed to load categories</p>';
            return [];
        }
    } catch (error) {
        console.error("Error loading categories:", error);
        container.innerHTML = '<p class="error">Network error</p>';
        return [];
    }
}

// Display categories
function displayCategories(categories, container, adminMode = false) {
    if (!categories || categories.length === 0) {
        container.innerHTML = '<p class="info">No categories found.</p>';
        return;
    }
    
    let html = '<div class="categories-grid">';
    for (const category of categories) {
        html += `
            <div class="category-card">
                <h3>${escapeHtml(category.name)}</h3>
                <div class="category-description">${escapeHtml(category.description?.substring(0, 150) || 'No description')}</div>
                <div class="category-stats">
                    <span class="product-count">📦 ${category.product_count || 0} products</span>
                </div>
                ${adminMode ? `
                    <div class="category-actions">
                        <button onclick="editCategory(${category.id})" class="btn btn-sm btn-outline">Edit</button>
                        <button onclick="deleteCategory(${category.id})" class="btn btn-sm btn-danger">Delete</button>
                    </div>
                ` : ''}
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

// Load categories for dropdown
async function loadCategoryDropdown(dropdownId, selectedId = null) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    
    try {
        const response = await fetch(API_ENDPOINTS.CATEGORIES);
        if (response.ok) {
            const categories = await response.json();
            
            dropdown.innerHTML = '<option value="">Select Category</option>';
            for (const category of categories) {
                const selected = selectedId == category.id ? 'selected' : '';
                dropdown.innerHTML += `<option value="${category.id}" ${selected}>${escapeHtml(category.name)}</option>`;
            }
        }
    } catch (error) {
        console.error("Error loading category dropdown:", error);
    }
}

// Create category (admin only)
async function createCategory(categoryData) {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_CATEGORIES, "POST", categoryData, true);
        if (response.ok) {
            const category = await response.json();
            showMessage(`Category "${category.name}" created successfully!`, "success");
            return category;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to create category", "error");
            return null;
        }
    } catch (error) {
        console.error("Error creating category:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Update category (admin only)
async function updateCategory(categoryId, categoryData) {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_CATEGORY(categoryId), "PUT", categoryData, true);
        if (response.ok) {
            const category = await response.json();
            showMessage(`Category "${category.name}" updated successfully!`, "success");
            return category;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to update category", "error");
            return null;
        }
    } catch (error) {
        console.error("Error updating category:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Delete category (admin only)
async function deleteCategory(categoryId) {
    if (!confirm("Are you sure you want to delete this category? Products will lose their category assignment.")) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_CATEGORY(categoryId), "DELETE", null, true);
        if (response.ok) {
            showMessage("Category deleted successfully!", "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to delete category", "error");
        }
    } catch (error) {
        console.error("Error deleting category:", error);
        showMessage("Network error", "error");
    }
}

// Edit category modal
function editCategory(categoryId) {
    showMessage(`Edit category ${categoryId} - Modal would open here`, "info");
    // In production, you would open a modal with category form
}