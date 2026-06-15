/**
 * Order Management Functions
 * Handles order listing, creation, status updates
 */

// Load orders
async function loadOrders(containerId, userId = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading orders...</p></div>';
    
    try {
        let url;
        if (isAdmin()) {
            url = API_ENDPOINTS.ADMIN_ORDERS;
        } else {
            const user = getCurrentUser();
            url = API_ENDPOINTS.USER_ORDERS(user?.id);
        }
        
        const response = await apiCall(url, "GET", null, true);
        
        if (response.ok) {
            const orders = await response.json();
            displayOrders(orders, container);
            return orders;
        } else {
            container.innerHTML = '<p class="error">Failed to load orders</p>';
            return [];
        }
    } catch (error) {
        console.error("Error loading orders:", error);
        container.innerHTML = '<p class="error">Network error</p>';
        return [];
    }
}

// Display orders
function displayOrders(orders, container) {
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p class="info">No orders found.</p>';
        return;
    }
    
    let html = '<div class="orders-list">';
    for (const order of orders) {
        const statusClass = order.status.toLowerCase();
        html += `
            <div class="order-card">
                <div class="order-header">
                    <h3>Order #${order.id}</h3>
                    <span class="order-status ${statusClass}">${order.status}</span>
                </div>
                <div class="order-details">
                    <div>
                        <strong>Order Date</strong>
                        <p>${formatDate(order.created_at)}</p>
                    </div>
                    <div>
                        <strong>Total Amount</strong>
                        <p>${formatCurrency(order.total_amount)}</p>
                    </div>
                    <div>
                        <strong>Items</strong>
                        <p>${order.item_count || order.items?.length || 0}</p>
                    </div>
                </div>
                <div class="order-items">
                    <h4>Order Items</h4>
                    ${displayOrderItems(order.items)}
                </div>
                ${isAdmin() ? `
                    <div class="order-actions">
                        <select id="status-${order.id}" class="status-select">
                            <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>Pending</option>
                            <option value="Processing" ${order.status === 'Processing' ? 'selected' : ''}>Processing</option>
                            <option value="Shipped" ${order.status === 'Shipped' ? 'selected' : ''}>Shipped</option>
                            <option value="Delivered" ${order.status === 'Delivered' ? 'selected' : ''}>Delivered</option>
                            <option value="Cancelled" ${order.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                        <button onclick="updateOrderStatus(${order.id})" class="btn btn-sm btn-primary">Update Status</button>
                        ${order.status !== 'Cancelled' ? `<button onclick="cancelOrder(${order.id})" class="btn btn-sm btn-danger">Cancel Order</button>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

// Display order items
function displayOrderItems(items) {
    if (!items || items.length === 0) {
        return '<p>No items in this order</p>';
    }
    
    let html = '<ul>';
    for (const item of items) {
        html += `
            <li>
                <div class="item-info">
                    <strong>${escapeHtml(item.product_name || `Product #${item.product_id}`)}</strong>
                    <span>Quantity: ${item.quantity}</span>
                    <span>Price: ${formatCurrency(item.price)}</span>
                    <span>Subtotal: ${formatCurrency(item.subtotal || (item.price * item.quantity))}</span>
                </div>
            </li>
        `;
    }
    html += '</ul>';
    return html;
}

// Create order
async function createOrder(userId, items) {
    try {
        const response = await apiCall(API_ENDPOINTS.ORDERS, "POST", {
            user_id: userId,
            items: items
        }, true);
        
        if (response.ok) {
            const order = await response.json();
            showMessage(`Order #${order.id} created successfully!`, "success");
            return order;
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to create order", "error");
            return null;
        }
    } catch (error) {
        console.error("Error creating order:", error);
        showMessage("Network error", "error");
        return null;
    }
}

// Update order status (admin only)
async function updateOrderStatus(orderId) {
    const select = document.getElementById(`status-${orderId}`);
    const newStatus = select?.value;
    
    if (!newStatus) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.UPDATE_ORDER_STATUS(orderId, newStatus), "PUT", null, true);
        if (response.ok) {
            showMessage(`Order #${orderId} status updated to ${newStatus}`, "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to update order status", "error");
        }
    } catch (error) {
        console.error("Error updating order status:", error);
        showMessage("Network error", "error");
    }
}

// Cancel order (admin only)
async function cancelOrder(orderId) {
    if (!confirm("Are you sure you want to cancel this order? Stock will be restored.")) return;
    
    try {
        const response = await apiCall(API_ENDPOINTS.CANCEL_ORDER(orderId), "POST", null, true);
        if (response.ok) {
            showMessage(`Order #${orderId} cancelled successfully`, "success");
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || "Failed to cancel order", "error");
        }
    } catch (error) {
        console.error("Error cancelling order:", error);
        showMessage("Network error", "error");
    }
}

// Filter orders by status (admin only)
async function filterOrdersByStatus(status) {
    const container = document.getElementById("ordersContainer");
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Filtering orders...</p></div>';
    
    try {
        let url = API_ENDPOINTS.ADMIN_ORDERS;
        if (status && status !== "all") {
            url += `?status_filter=${status}`;
        }
        
        const response = await apiCall(url, "GET", null, true);
        if (response.ok) {
            const orders = await response.json();
            displayOrders(orders, container);
        }
    } catch (error) {
        console.error("Error filtering orders:", error);
        container.innerHTML = '<p class="error">Filter failed</p>';
    }
}