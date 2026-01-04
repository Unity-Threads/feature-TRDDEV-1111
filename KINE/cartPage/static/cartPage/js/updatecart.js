// ===============================
// CART FUNCTIONALITY + SELECTION
// ===============================
let currentCODStatus = true; // Whether all items are COD eligible

document.addEventListener("DOMContentLoaded", () => {
    setupSelectionFeature();
    updateCartSummary();
});

// ------------------------------
// EVENT DELEGATION FOR QUANTITY BUTTONS
// ------------------------------
document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("qty-btn")) {
        const button = e.target;
        const itemId = button.dataset.id;
        const action = button.classList.contains("increase") ? "increase" : "decrease";

        const qtyDisplay = document.querySelector(`#qty-${itemId}`);
        if (!qtyDisplay) return;

        let currentQty = parseInt(qtyDisplay.textContent || qtyDisplay.value);

        if (action === "increase") currentQty++;
        else if (action === "decrease" && currentQty > 1) currentQty--;

        // Update locally
        if (qtyDisplay.tagName === "INPUT") {
            qtyDisplay.value = currentQty;
        } else {
            qtyDisplay.textContent = currentQty;
        }
        // After updating quantity
        const qtySpan = document.getElementById(`qty-${itemId}`);
        const newQty = parseInt(qtySpan.textContent);

        const increaseBtn = document.querySelector(`.increase[data-id="${itemId}"]`);
        const stock = parseInt(increaseBtn.dataset.stock);

        // Disable + button if stock reached
        if (newQty >= stock) {
            increaseBtn.disabled = true;
        } else {
            increaseBtn.disabled = false;
        }

        // ✅ Wait for backend update to complete before refreshing summary
        await updateCart(itemId, action);
    }
});

// ------------------------------
// UPDATE CART VIA AJAX
// ------------------------------
async function updateCart(itemId, action) {
    try {
        const response = await fetch(`/update-cart/${itemId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ action })
        });

        if (!response.ok) throw new Error("Network error");
        const data = await response.json();

        if (data.removed) {
            const itemRow = document.querySelector(`#qty-${itemId}`)?.closest(".cart-item");
            if (itemRow) itemRow.remove();
        } else {
            const qtyEl = document.querySelector(`#qty-${itemId}`);
            if (qtyEl) qtyEl.textContent = data.quantity;

            const subtotalEl = document.querySelector(`#subtotal-${itemId}`);
            if (subtotalEl) {
                const rawSubtotal = data.subtotal ?? data.sub_total ?? 0;
                subtotalEl.textContent = formatCurrency(parseNumber(rawSubtotal), false);
            }
        }

        // ✅ Handle COD eligibility toggle

        const codInput = document.getElementById("payment-cod");
        if (codInput && data.hasOwnProperty("all_items_eligible_for_cod")) {
            currentCODStatus = data.all_items_eligible_for_cod;
            if (currentCODStatus) {
                codInput.disabled = false;
                codInput.style.cursor = "pointer";
                codInput.title = "";
            } else {
                codInput.disabled = true;
                codInput.checked = false;
                codInput.style.cursor = "not-allowed";
                codInput.title = "Some items are not eligible for Cash on Delivery.";
            }
        }

        // ✅ Update summary after backend updates are applied
        updateCartSummary();

    } catch (error) {
        console.error("Error updating cart:", error);
    }
}

// ------------------------------
// SELECTION FEATURE + SELECT ALL
// ------------------------------
function setupSelectionFeature() {
    const checkboxes = document.querySelectorAll(".select-item");
    const selectAllCheckbox = document.getElementById("select-all");
    const checkoutButton = document.getElementById("checkout-button");

    checkboxes.forEach(box => box.addEventListener("change", updateCartSummary));

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            checkboxes.forEach(box => (box.checked = selectAllCheckbox.checked));
            updateCartSummary();
        });
    }

    if (checkoutButton) {
        checkoutButton.addEventListener("click", function (e) {
            const selectedItems = getSelectedItemIDs();
            const warningMessage = document.getElementById("warning-message");

            if (selectedItems.length === 0) {
                e.preventDefault();
                if (warningMessage) {
                    warningMessage.textContent = "⚠️ Please select at least one item before placing the order.";
                    warningMessage.style.display = "block";
                    warningMessage.scrollIntoView({ behavior: "smooth" });
                }
            } else {
                if (warningMessage) warningMessage.style.display = "none";
                placeSelectedOrder(selectedItems);
            }
        });
    }

    const observer = new MutationObserver(updateCartSummary);
    document.querySelectorAll(".cart-item-subtotal").forEach(el =>
        observer.observe(el, { childList: true })
    );
}

// ------------------------------
// UPDATE CART SUMMARY
// ------------------------------
function updateCartSummary() {
    const checkboxes = document.querySelectorAll(".select-item");
    const warningMessage = document.getElementById("warning-message");
    const codInput = document.getElementById("payment-cod");

    const taxRateEl = document.getElementById("tax-rate");
    const baseDeliveryEl = document.getElementById("delivery-charge-base");
    const minAmountEl = document.getElementById("min-amount-for-free-delivery");

    const taxRate = taxRateEl ? parseNumber(taxRateEl.value) : 0;
    const baseDeliveryCharge = baseDeliveryEl ? parseNumber(baseDeliveryEl.value) : 0;
    const minAmountForFreeDelivery = minAmountEl ? parseNumber(minAmountEl.value) : 0;

    let total = 0;
    let totalItems = 0;
    let all_items_eligible_for_cod = true;

    checkboxes.forEach(box => {
        if (box.checked) {
            const itemId = box.dataset.id;
            const subtotalEl = document.querySelector(`#subtotal-${itemId}`);
            const qtyEl = document.querySelector(`#qty-${itemId}`);

            const qty = qtyEl ? parseInt(qtyEl.textContent || qtyEl.value || 0) : 0;
            const subtotal = subtotalEl ? parseNumber(subtotalEl.textContent) : 0;

            total += subtotal;
            totalItems += qty;

            if (box.dataset.cod !== "true") {
                all_items_eligible_for_cod = false;
            }
        }
    });

    // ✅ Enable/disable COD dynamically
    if (codInput) {
        if (totalItems === 0) {
            codInput.disabled = true;
            codInput.checked = false;
            codInput.style.cursor = "not-allowed";
            codInput.title = "No items selected.";
        } else if (all_items_eligible_for_cod) {
            codInput.disabled = false;
            codInput.style.cursor = "pointer";
            codInput.title = "";
        } else {
            codInput.disabled = true;
            codInput.checked = false;
            codInput.style.cursor = "not-allowed";
            codInput.title = "Some selected items are not eligible for Cash on Delivery.";
        }
    }

    if (totalItems === 0) {
        if (warningMessage) {
            warningMessage.textContent = "⚠️ Please select at least one item to update summary.";
            warningMessage.style.display = "block";
        }
        setSummaryDisplays(0, 0, 0, 0, 0);
        return;
    } else {
        if (warningMessage) warningMessage.style.display = "none";
    }

    const tax = (taxRate / 100) * total;
    const deliveryCharge = (total >= minAmountForFreeDelivery) ? 0 : baseDeliveryCharge;
    const grandTotal = total + tax + deliveryCharge;

    setSummaryDisplays(total, totalItems, tax, deliveryCharge, grandTotal);
}

// ------------------------------
// SUMMARY DISPLAY UPDATE
// ------------------------------

function setSummaryDisplays(total, count, tax, deliveryCharge, grandTotal) {
    const totalDisplay = document.getElementById("total-price");
    const summaryItems = document.getElementById("total-items");
    const taxesEl = document.getElementById("taxes");
    const deliveryEl = document.getElementById("delivery-charge");
    const grandTotalEl = document.getElementById("grand-total");

    if (totalDisplay) totalDisplay.textContent = formatCurrency(total, false);
    if (summaryItems) summaryItems.textContent = count;
    if (taxesEl) taxesEl.textContent = formatCurrency(tax, false);
    if (deliveryEl) deliveryEl.textContent = formatCurrency(deliveryCharge, false);
    if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grandTotal, false);
}

// ------------------------------
// UTILITIES
// ------------------------------
function parseNumber(value) {
    return parseFloat(value.toString().replace(/[^\d.-]/g, '')) || 0;
}

function formatCurrency(amount, includeSymbol = true) {
    if (amount === null || amount === undefined || isNaN(amount)) return includeSymbol ? "₹0.00" : "0.00";
    return includeSymbol ? `₹${Number(amount).toFixed(2)}` : Number(amount).toFixed(2);
}

function getSelectedItemIDs() {
    return Array.from(document.querySelectorAll(".select-item"))
        .filter(box => box.checked)
        .map(box => box.dataset.id);
}

function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name)) return trimmed.substring(name.length);
    }
    return "";
}


// -----------------------------------------------------------
// ADDRESS DROPDOWN — HANDLE OPTION CLICK + UPDATE HIDDEN INPUT
// -----------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const selectedOption = document.querySelector(".selected-option");
    const options = document.querySelectorAll(".option");
    const hiddenAddressInput = document.getElementById("selected_address_input");

    // Toggle dropdown visibility
    document.getElementById("selected_address").addEventListener("click", function () {
        this.classList.toggle("open");
    });

    // When user selects an address
    options.forEach(opt => {
        opt.addEventListener("click", function () {

            // Update visible text in the dropdown
            selectedOption.innerHTML = this.innerHTML;

            // Update hidden input value
            hiddenAddressInput.value = this.dataset.id;

            // Close dropdown
            document.getElementById("selected_address").classList.remove("open");
        });
    });
});


// ---------------------------------------------
// GET SELECTED ADDRESS FROM HIDDEN INPUT
// ---------------------------------------------
function getSelectedAddressId() {
    const addressId = document.getElementById("selected_address_input").value;
    console.log("Selected Address ID:", addressId);
    return addressId || null;
}

// -----------------------------------------------------------
// PLACE ORDER — SEND ITEMS + ADDRESS + PAYMENT METHOD
// -----------------------------------------------------------
async function placeSelectedOrder(selectedItems) {
    try {
        const addressId = getSelectedAddressId();
        const paymentMethod = document.querySelector(
            'input[name="payment_method"]:checked'
        ).value;

        const response = await fetch("/orders/confirm_order/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                selected_items: selectedItems,
                selected_address: addressId,
                payment_method: paymentMethod
            })
        });

        const data = await response.json();

        if (data.redirect_url) {
            // ✅ BOTH COD & PREPAID go to confirm page
            window.location.href = data.redirect_url;
        }

    } catch (err) {
        console.error("Order Error:", err);
        alert("❌ Error placing order. Try again.");
    }
}


