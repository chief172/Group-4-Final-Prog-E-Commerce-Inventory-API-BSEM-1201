/**
 * Product Management Functions
 * Handles product listing, creation, editing, deletion
 */

// Load all products
async function loadProducts(containerId, adminMode = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading products...</p></div>';
    
    try {
        const url = adminMode ? API_ENDPOINTS.ADMIN_PRODUCTS : API_ENDPOINTS.PRODUCTS;
        const response = await apiCall(url, "GET", null, adminMode);
        
        if (response.ok) {
            const products = await response.json();
            displayProducts(products, container, adminMode);
            return products;
        } else {
            container.innerHTML = '<p class="error">Failed to load products</p>';
            return [];
        }
    } catch (error) {
        console.error("Error loading products:", error);
        container.innerHTML = '<p class="error">Network error. Please try again.</p>';
        return [];
    }
}

// Display products
function displayProducts(products, container, adminMode = false) {
    if (!products || products.length === 0) {
        container.innerHTML = '<p class="info">No products found.</p>';
        return;
    }
    
    let html = '<div class="products-grid">';
    for (const product of products) {
        const stockClass = product.stock_quantity === 0 ? 'out' : (product.stock_quantity < 5 ? 'low' : '');
        html += `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-image">
                    📦
                </div>
                <div class="product-info">
                    <h3>${escapeHtml(product.name)}</h3>
                    <div class="product-price">${formatCurrency(product.price)}</div>
                    <div class="product-stock ${stockClass}">
                        Stock: ${product.stock_quantity} units
                        ${product.stock_quantity < 5 && product.stock_quantity > 0 ? '<span class="warning-badge">Low Stock!</span>' : ''}
                        ${product.stock_quantity === 0 ? '<span class="danger-badge">Out of Stock!</span>' : ''}
                    </div>
                    <div class="product-description">${escapeHtml(product.description?.substring(0, 100) || 'No description')}${product.description?.length > 100 ? '...' : ''}</div>
                    <div class="product-category">Category: ${escapeHtml(product.category_name || `ID: ${product.category_id}`)}</div>
                    ${adminMode ? `
                        <div class="product-actions">
                            <button onclick="editProduct(${product.id})" class="btn btn-sm btn-outline">Edit</button>
                            <button onclick="deleteProduct(${product.id})" class="btn btn-sm btn-danger">Delete</button>
                            <button onclick="updateStock(${product.id})" class="btn btn-sm btn-warning">Update Stock</button>
                        </div>
                    ` : `
                        <div class="product-actions">
                            <button onclick="addToCart(${product.id})" class="btn btn-sm btn-primary" ${product.stock_quantity === 0 ? 'disabled' : ''}>Add to Cart</button>
                        </div>
                    `}
                </div>
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

// Create product (admin only)
async function createProduct(productData) {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_PRODUCTS, "POST", productData, true);
        if (response.ok) {
            const product = await response.json();
            showMessage(`Product "${product.name}" created successfully!`, "success");
            return product;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to create product", "error");
            return null;
        }
    } catch (error) {
        console.error("Error creating product:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Update product (admin only)
async function updateProduct(productId, productData) {
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_PRODUCT(productId), "PUT", productData, true);
        if (response.ok) {
            const product = await response.json();
            showMessage(`Product "${product.name}" updated successfully!`, "success");
            return product;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to update product", "error");
            return null;
        }
    } catch (error) {
        console.error("Error updating product:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Delete product (admin only)
async function deleteProduct(productId) {
    if (!confirm("Are you sure you want to delete this product? This action cannot be undone.")) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_PRODUCT(productId), "DELETE", null, true);
        if (response.ok) {
            showMessage("Product deleted successfully!", "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to delete product", "error");
        }
    } catch (error) {
        console.error("Error deleting product:", error);
        showMessage("Network error", "error");
    }
}

// Update stock (admin only)
async function updateStock(productId) {
    const newStock = prompt("Enter new stock quantity:");
    if (newStock === null) return;
    
    const quantity = parseInt(newStock);
    if (isNaN(quantity) || quantity < 0) {
        showMessage("Please enter a valid positive number", "error");
        return;
    }
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADMIN_PRODUCT(productId), "PUT", { stock_quantity: quantity }, true);
        if (response.ok) {
            showMessage("Stock updated successfully!", "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to update stock", "error");
        }
    } catch (error) {
        console.error("Error updating stock:", error);
        showMessage("Network error", "error");
    }
}

// Search products
async function searchProducts(searchTerm) {
    if (!searchTerm || searchTerm.trim() === "") {
        return await loadProducts("productsContainer", isAdmin());
    }
    
    const container = document.getElementById("productsContainer");
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Searching...</p></div>';
    
    try {
        const response = await fetch(`${API_ENDPOINTS.PRODUCTS}?search=${encodeURIComponent(searchTerm)}`);
        if (response.ok) {
            const products = await response.json();
            displayProducts(products, container, isAdmin());
            return products;
        }
    } catch (error) {
        console.error("Error searching products:", error);
        container.innerHTML = '<p class="error">Search failed</p>';
    }
    return [];
}

// Filter products by category
async function filterByCategory(categoryId) {
    const container = document.getElementById("productsContainer");
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Filtering...</p></div>';
    
    try {
        let url = API_ENDPOINTS.PRODUCTS;
        if (categoryId && categoryId !== "all") {
            url += `?category_id=${categoryId}`;
        }
        const response = await fetch(url);
        if (response.ok) {
            const products = await response.json();
            displayProducts(products, container, isAdmin());
            return products;
        }
    } catch (error) {
        console.error("Error filtering products:", error);
        container.innerHTML = '<p class="error">Filter failed</p>';
    }
    return [];
}

// Edit product modal
function editProduct(productId) {
    // Get product data and populate modal
    showMessage(`Edit product ${productId} - Modal would open here`, "info");
    // In production, you would open a modal with product form
}

// Add to cart
async function addToCart(productId) {
    if (!isAuthenticated()) {
        showMessage("Please login to add items to cart", "warning");
        setTimeout(() => window.location.href = "/login.html", 1500);
        return;
    }
    
    const user = getCurrentUser();
    const quantity = prompt("Enter quantity:", "1");
    
    if (!quantity) return;
    
    const qty = parseInt(quantity);
    if (isNaN(qty) || qty < 1) {
        showMessage("Please enter a valid quantity", "error");
        return;
    }
    
    try {
        const response = await apiCall(API_ENDPOINTS.ADD_TO_CART, "POST", {
            user_id: user.id,
            product_id: productId,
            quantity: qty
        }, true);
        
        if (response.ok) {
            showMessage("Product added to cart successfully!", "success");
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to add to cart", "error");
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
        showMessage("Network error", "error");
    }
}