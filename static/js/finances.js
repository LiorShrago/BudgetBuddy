// Unified finances page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    initializePage();
    setupEventListeners();
    loadAccountTransactions();
    
    // Initialize feather icons
    feather.replace();
});

// Global variables
let selectedTransactions = new Set();
let currentFilters = {
    accountType: 'all',
    category: 'all',
    dateRange: '30days',
    transactionType: 'all',
    dateFrom: null,
    dateTo: null,
    amountMin: null,
    amountMax: null,
    description: null
};

function initializePage() {
    // Set default date for date inputs
    setDefaultDateRange();
    
    // Initialize account edit/delete buttons
    initializeAccountButtons();
    
    // Load category overview
    loadCategoryOverview();
    
    // Load uncategorized transactions summary
    loadUncategorizedSummary();
}

function setupEventListeners() {
    // Toggle advanced filters
    document.getElementById('toggle-advanced-filters').addEventListener('click', toggleAdvancedFilters);
    
    // Date range change
    document.getElementById('date-range-filter').addEventListener('change', handleDateRangeChange);
    
    // Filter button
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    
    // Quick filter buttons
    document.querySelectorAll('.quick-filter').forEach(button => {
        button.addEventListener('click', applyQuickFilter);
    });
    
    // Collapse/expand all accounts
    document.getElementById('collapse-all-accounts').addEventListener('click', collapseAllAccounts);
    document.getElementById('expand-all-accounts').addEventListener('click', expandAllAccounts);
    
    // Add transaction buttons
    document.querySelectorAll('.add-transaction-btn').forEach(button => {
        button.addEventListener('click', showAddTransactionModal);
    });
    
    // Add transaction form submission
    document.getElementById('add-transaction-form').addEventListener('submit', handleAddTransaction);
    
    // Bulk categorize button
    document.getElementById('confirm-bulk-categorize').addEventListener('click', handleBulkCategorize);
    
    // AI suggestions buttons
    document.getElementById('accept-all-suggestions').addEventListener('click', acceptAllSuggestions);
    document.getElementById('apply-suggestions').addEventListener('click', applySelectedSuggestions);
    
    // New categorization features
    document.getElementById('quick-categorize-mode').addEventListener('click', openQuickCategorizePanel);
    document.getElementById('ai-auto-categorize').addEventListener('click', autoCategorizeTranactions);
    document.getElementById('categorize-all-uncategorized').addEventListener('click', categorizeAllUncategorized);
    
    // Enable delete account button only when "DELETE" is typed
    document.getElementById('confirm_delete').addEventListener('input', function(e) {
        const deleteBtn = document.getElementById('confirm_delete_btn');
        deleteBtn.disabled = e.target.value !== 'DELETE';
    });
}

function setDefaultDateRange() {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    document.getElementById('date-from').valueAsDate = thirtyDaysAgo;
    document.getElementById('date-to').valueAsDate = today;
}

function toggleAdvancedFilters() {
    const advancedFilters = document.getElementById('advanced-filters');
    const moreFiltersText = document.querySelector('.more-filters');
    const lessFiltersText = document.querySelector('.less-filters');
    
    if (advancedFilters.style.display === 'none' || !advancedFilters.style.display) {
        advancedFilters.style.display = 'flex';
        moreFiltersText.style.display = 'none';
        lessFiltersText.style.display = 'inline';
    } else {
        advancedFilters.style.display = 'none';
        moreFiltersText.style.display = 'inline';
        lessFiltersText.style.display = 'none';
    }
}

function handleDateRangeChange() {
    const dateRange = document.getElementById('date-range-filter').value;
    const customDateRange = document.getElementById('custom-date-range');
    
    if (dateRange === 'custom') {
        customDateRange.style.display = 'flex';
    } else {
        customDateRange.style.display = 'none';
        setDateRangeFromPreset(dateRange);
    }
}

function setDateRangeFromPreset(preset) {
    const today = new Date();
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');
    
    dateTo.valueAsDate = today;
    
    switch (preset) {
        case '7days':
            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(today.getDate() - 7);
            dateFrom.valueAsDate = sevenDaysAgo;
            break;
        case '30days':
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(today.getDate() - 30);
            dateFrom.valueAsDate = thirtyDaysAgo;
            break;
        case '90days':
            const ninetyDaysAgo = new Date();
            ninetyDaysAgo.setDate(today.getDate() - 90);
            dateFrom.valueAsDate = ninetyDaysAgo;
            break;
        case 'year':
            const startOfYear = new Date(today.getFullYear(), 0, 1);
            dateFrom.valueAsDate = startOfYear;
            break;
        case 'all':
            dateFrom.value = '';
            dateTo.value = '';
            break;
    }
}

function applyFilters() {
    // Gather filter values
    currentFilters.accountType = document.getElementById('account-type-filter').value;
    currentFilters.category = document.getElementById('transaction-category-filter').value;
    currentFilters.dateRange = document.getElementById('date-range-filter').value;
    currentFilters.transactionType = document.getElementById('transaction-type-filter').value;
    currentFilters.dateFrom = document.getElementById('date-from').value;
    currentFilters.dateTo = document.getElementById('date-to').value;
    currentFilters.amountMin = document.getElementById('amount-min').value || null;
    currentFilters.amountMax = document.getElementById('amount-max').value || null;
    currentFilters.description = document.getElementById('description-search').value || null;
    
    // Filter accounts based on account type
    filterAccounts();
    
    // Reload transactions with new filters
    loadAccountTransactions();
    
    // Show filters applied message
    showAlert('Filters applied successfully', 'success');
}

function filterAccounts() {
    const accountItems = document.querySelectorAll('.account-item');
    const accountType = currentFilters.accountType;
    
    accountItems.forEach(item => {
        if (accountType === 'all' || item.dataset.accountType === accountType) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function applyQuickFilter(event) {
    const filterType = event.currentTarget.dataset.filter;
    
    // Reset all inputs first
    document.getElementById('account-type-filter').value = 'all';
    document.getElementById('transaction-category-filter').value = 'all';
    document.getElementById('date-range-filter').value = '30days';
    document.getElementById('transaction-type-filter').value = 'all';
    document.getElementById('amount-min').value = '';
    document.getElementById('amount-max').value = '';
    document.getElementById('description-search').value = '';
    
    switch (filterType) {
        case 'recent':
            document.getElementById('date-range-filter').value = '7days';
            handleDateRangeChange();
            break;
        case 'high-value':
            document.getElementById('amount-min').value = '100';
            document.getElementById('advanced-filters').style.display = 'flex';
            document.querySelector('.more-filters').style.display = 'none';
            document.querySelector('.less-filters').style.display = 'inline';
            break;
        case 'uncategorized':
            document.getElementById('transaction-category-filter').value = 'uncategorized';
            break;
        case 'food':
            // Assuming there's a category named "Food & Dining" or similar
            const foodOption = Array.from(document.getElementById('transaction-category-filter').options).find(
                option => option.text.toLowerCase().includes('food') || option.text.toLowerCase().includes('dining')
            );
            if (foodOption) document.getElementById('transaction-category-filter').value = foodOption.value;
            break;
        case 'shopping':
            // Assuming there's a category named "Shopping" or similar
            const shoppingOption = Array.from(document.getElementById('transaction-category-filter').options).find(
                option => option.text.toLowerCase().includes('shopping')
            );
            if (shoppingOption) document.getElementById('transaction-category-filter').value = shoppingOption.value;
            break;
        case 'reset':
            setDefaultDateRange();
            handleDateRangeChange();
            break;
    }
    
    // Apply the filters
    applyFilters();
}

function collapseAllAccounts() {
    document.querySelectorAll('.accordion-collapse').forEach(item => {
        item.classList.remove('show');
    });
    document.querySelectorAll('.accordion-button').forEach(item => {
        item.classList.add('collapsed');
    });
}

function expandAllAccounts() {
    document.querySelectorAll('.accordion-collapse').forEach(item => {
        item.classList.add('show');
    });
    document.querySelectorAll('.accordion-button').forEach(item => {
        item.classList.remove('collapsed');
    });
}

// Account handling functions
function initializeAccountButtons() {
    // Edit account buttons
    document.querySelectorAll('.edit-account').forEach(button => {
        button.addEventListener('click', function() {
            const accountId = this.dataset.accountId;
            editAccount(accountId);
        });
    });
    
    // Delete account buttons
    document.querySelectorAll('.delete-account').forEach(button => {
        button.addEventListener('click', function() {
            const accountId = this.dataset.accountId;
            const accountName = this.dataset.accountName;
            confirmDeleteAccount(accountId, accountName);
        });
    });
}

function editAccount(accountId) {
    // Fetch account data from the DOM or make an API call
    const accountElement = document.querySelector(`.account-item[data-account-id="${accountId}"]`);
    const accountName = accountElement.querySelector('.accordion-button .fw-bold').textContent;
    const accountType = accountElement.dataset.accountType;
    const accountBalance = accountElement.querySelector('.text-success, .text-danger').textContent.replace('$', '');
    const isActive = accountElement.querySelector('.badge.bg-success, .badge.bg-danger').textContent.trim() === 'Active';
    
    // Populate edit form
    document.getElementById('edit_account_id').value = accountId;
    document.getElementById('edit_name').value = accountName;
    document.getElementById('edit_account_type').value = accountType;
    document.getElementById('edit_balance').value = accountBalance;
    document.getElementById('edit_is_active').checked = isActive;
    
    // Show modal
    new bootstrap.Modal(document.getElementById('editAccountModal')).show();
}

function confirmDeleteAccount(accountId, accountName) {
    document.getElementById('delete_account_id').value = accountId;
    document.getElementById('delete_account_name').textContent = accountName;
    document.getElementById('confirm_delete').value = '';
    document.getElementById('confirm_delete_btn').disabled = true;
    
    new bootstrap.Modal(document.getElementById('deleteAccountModal')).show();
}

// Transaction handling functions
function loadAccountTransactions() {
    document.querySelectorAll('.account-item').forEach(accountItem => {
        if (accountItem.style.display !== 'none') {
            const accountId = accountItem.dataset.accountId;
            const container = document.getElementById(`transactions-${accountId}`);
            
            if (container) {
                // Show loading state
                container.innerHTML = `
                    <div class="text-center py-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Loading transactions...</p>
                    </div>
                `;
                
                // Fetch transactions from API
                fetchAccountTransactions(accountId)
                    .then(transactions => {
                        renderTransactions(accountId, transactions);
                    })
                    .catch(error => {
                        console.error('Error loading transactions:', error);
                        container.innerHTML = `
                            <div class="text-center py-3 text-danger">
                                <i data-feather="alert-circle" style="width: 24px; height: 24px;"></i>
                                <p>Error loading transactions. Please try again.</p>
                            </div>
                        `;
                        feather.replace();
                    });
            }
        }
    });
}

function fetchAccountTransactions(accountId) {
    // Build query parameters
    const params = new URLSearchParams();
    params.append('account', accountId);
    
    if (currentFilters.category && currentFilters.category !== 'all') {
        params.append('category', currentFilters.category);
    }
    
    if (currentFilters.transactionType && currentFilters.transactionType !== 'all') {
        params.append('type', currentFilters.transactionType);
    }
    
    if (currentFilters.dateFrom) {
        params.append('date_from', currentFilters.dateFrom);
    }
    
    if (currentFilters.dateTo) {
        params.append('date_to', currentFilters.dateTo);
    }
    
    if (currentFilters.amountMin) {
        params.append('amount_min', currentFilters.amountMin);
    }
    
    if (currentFilters.amountMax) {
        params.append('amount_max', currentFilters.amountMax);
    }
    
    if (currentFilters.description) {
        params.append('description', currentFilters.description);
    }
    
    // Make API request
    return fetch(`/api/account-transactions?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        });
}

function renderTransactions(accountId, data) {
    const container = document.getElementById(`transactions-${accountId}`);
    const transactions = data.transactions || [];
    
    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i data-feather="inbox" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                <h6>No Transactions Found</h6>
                <p class="text-muted">No transactions match your current filters, or this account has no transactions yet.</p>
                <button class="btn btn-sm btn-success add-transaction-btn" data-account-id="${accountId}">
                    <i data-feather="plus"></i> Add Transaction
                </button>
            </div>
        `;
        
        // Re-attach event listener
        container.querySelector('.add-transaction-btn').addEventListener('click', showAddTransactionModal);
        
        feather.replace();
        return;
    }
    
    // Render transactions table
    let html = `
        <div class="table-responsive">
            <table class="table table-hover transaction-table mb-0">
                <thead class="table-dark">
                    <tr>
                        <th style="width: 40px;">
                            <input type="checkbox" class="form-check-input select-all-transactions" data-account-id="${accountId}">
                        </th>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Category</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    transactions.forEach(transaction => {
        const isSelected = selectedTransactions.has(transaction.id);
        const formattedDate = new Date(transaction.date).toLocaleDateString();
        const descriptionClass = transaction.description.length > 30 ? 'transaction-description expandable' : 'transaction-description';
        const amountClass = transaction.transaction_type === 'expense' ? 'text-danger' : 'text-success';
        const amountPrefix = transaction.transaction_type === 'expense' ? '-' : '+';
        const categoryBadge = transaction.category ? 
            `<span class="badge" style="background-color: ${transaction.category.color};">${transaction.category.name}</span>` : 
            `<span class="badge bg-secondary">Uncategorized</span>`;
        
        html += `
            <tr data-transaction-id="${transaction.id}">
                <td>
                    <input type="checkbox" class="form-check-input transaction-checkbox" 
                           value="${transaction.id}" ${isSelected ? 'checked' : ''}>
                </td>
                <td>${formattedDate}</td>
                <td>
                    <div class="${descriptionClass}">${transaction.description.substring(0, 30)}${transaction.description.length > 30 ? '...' : ''}</div>
                    ${transaction.description.length > 30 ? 
                        `<small class="text-muted d-none full-description">${transaction.description}</small>` : ''}
                    ${transaction.merchant ? `<small class="text-muted">${transaction.merchant}</small>` : ''}
                </td>
                <td>
                    <span class="fw-bold ${amountClass}">${amountPrefix}$${parseFloat(transaction.amount).toFixed(2)}</span>
                </td>
                <td>
                    <select class="form-select form-select-sm category-select" data-transaction-id="${transaction.id}">
                        <option value="">Uncategorized</option>
                        ${renderCategoryOptions(transaction.category_id)}
                    </select>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary save-category" data-transaction-id="${transaction.id}">
                            <i data-feather="save"></i>
                        </button>
                        <button type="button" class="btn btn-outline-secondary edit-transaction" data-transaction-id="${transaction.id}">
                            <i data-feather="edit"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger delete-transaction" data-transaction-id="${transaction.id}">
                            <i data-feather="trash-2"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <div class="p-3 d-flex justify-content-between">
            <div>
                <span class="badge bg-secondary">${transactions.length} transactions</span>
                <span class="selected-count-badge badge bg-primary" id="selected-count-${accountId}">0 selected</span>
            </div>
            <div class="btn-group">
                <button type="button" class="btn btn-sm btn-outline-info ai-suggest-btn" data-account-id="${accountId}" disabled>
                    <i data-feather="star"></i> AI Suggest
                </button>
                <button type="button" class="btn btn-sm btn-outline-success categorize-selected-btn" data-account-id="${accountId}" disabled>
                    <i data-feather="tag"></i> Categorize Selected
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Add event listeners for the new elements
    initializeTransactionEvents(accountId);
    
    // Update selected count
    updateSelectedCount(accountId);
    
    // Replace feather icons
    feather.replace();
}

function renderCategoryOptions(selectedCategoryId) {
    // This should match with the categories in the page
    const categoriesSelect = document.getElementById('transaction-category-filter');
    let optionsHtml = '';
    
    for (let i = 1; i < categoriesSelect.options.length; i++) {
        if (categoriesSelect.options[i].value !== 'uncategorized') {
            const option = categoriesSelect.options[i];
            const isSelected = option.value === selectedCategoryId;
            optionsHtml += `<option value="${option.value}" ${isSelected ? 'selected' : ''}>${option.text}</option>`;
        }
    }
    
    return optionsHtml;
}

function showAddTransactionModal(event) {
    const accountId = event.currentTarget.dataset.accountId;
    
    // Set account ID in form
    document.getElementById('transaction_account_id').value = accountId;
    
    // Set default date to today
    document.getElementById('transaction_date').valueAsDate = new Date();
    
    // Reset form
    document.getElementById('add-transaction-form').reset();
    document.getElementById('transaction_account_id').value = accountId;
    
    // Show modal
    new bootstrap.Modal(document.getElementById('addTransactionModal')).show();
}

function initializeTransactionEvents(accountId) {
    // Select all checkbox for this account
    const selectAllCheckbox = document.querySelector(`.select-all-transactions[data-account-id="${accountId}"]`);
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            const transactionCheckboxes = document.querySelectorAll(`#transactions-${accountId} .transaction-checkbox`);
            
            transactionCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                updateSelectedTransactionState(checkbox.value, isChecked);
            });
            
            updateSelectedCount(accountId);
        });
    }
    
    // Individual transaction checkboxes
    const transactionCheckboxes = document.querySelectorAll(`#transactions-${accountId} .transaction-checkbox`);
    transactionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedTransactionState(this.value, this.checked);
            updateSelectedCount(accountId);
        });
    });
    
    // Category selects
    document.querySelectorAll(`#transactions-${accountId} .category-select`).forEach(select => {
        select.addEventListener('change', function() {
            const saveBtn = document.querySelector(`.save-category[data-transaction-id="${this.dataset.transactionId}"]`);
            saveBtn.classList.remove('btn-outline-primary');
            saveBtn.classList.add('btn-warning');
        });
    });
    
    // Save category buttons
    document.querySelectorAll(`#transactions-${accountId} .save-category`).forEach(btn => {
        btn.addEventListener('click', function() {
            const transactionId = this.dataset.transactionId;
            const categorySelect = document.querySelector(`.category-select[data-transaction-id="${transactionId}"]`);
            const categoryId = categorySelect.value;
            
            updateTransactionCategory(transactionId, categoryId, this);
        });
    });
    
    // Edit transaction buttons
    document.querySelectorAll(`#transactions-${accountId} .edit-transaction`).forEach(btn => {
        btn.addEventListener('click', function() {
            const transactionId = this.dataset.transactionId;
            editTransaction(transactionId);
        });
    });
    
    // Delete transaction buttons
    document.querySelectorAll(`#transactions-${accountId} .delete-transaction`).forEach(btn => {
        btn.addEventListener('click', function() {
            const transactionId = this.dataset.transactionId;
            deleteTransaction(transactionId);
        });
    });
    
    // Expandable descriptions
    document.querySelectorAll(`#transactions-${accountId} .transaction-description.expandable`).forEach(desc => {
        desc.addEventListener('click', function() {
            const fullDesc = this.parentNode.querySelector('.full-description');
            if (fullDesc) {
                if (fullDesc.classList.contains('d-none')) {
                    this.textContent = fullDesc.textContent;
                    fullDesc.classList.remove('d-none');
                } else {
                    this.textContent = fullDesc.textContent.substring(0, 30) + '...';
                    fullDesc.classList.add('d-none');
                }
            }
        });
    });
    
    // AI suggest button
    const aiSuggestBtn = document.querySelector(`#transactions-${accountId} .ai-suggest-btn`);
    if (aiSuggestBtn) {
        aiSuggestBtn.addEventListener('click', function() {
            const accountId = this.dataset.accountId;
            const selectedIds = getSelectedTransactionIds(accountId);
            requestAiSuggestions(selectedIds);
        });
    }
    
    // Categorize selected button
    const categorizeSelectedBtn = document.querySelector(`#transactions-${accountId} .categorize-selected-btn`);
    if (categorizeSelectedBtn) {
        categorizeSelectedBtn.addEventListener('click', function() {
            const accountId = this.dataset.accountId;
            const selectedIds = getSelectedTransactionIds(accountId);
            showBulkCategorizeModal(selectedIds);
        });
    }
}

function updateSelectedTransactionState(transactionId, isSelected) {
    if (isSelected) {
        selectedTransactions.add(transactionId);
    } else {
        selectedTransactions.delete(transactionId);
    }
}

function updateSelectedCount(accountId) {
    const selectedCount = getSelectedTransactionIds(accountId).length;
    const selectedCountBadge = document.getElementById(`selected-count-${accountId}`);
    if (selectedCountBadge) {
        selectedCountBadge.textContent = `${selectedCount} selected`;
    }
    
    // Enable/disable buttons based on selection
    const aiSuggestBtn = document.querySelector(`#transactions-${accountId} .ai-suggest-btn`);
    const categorizeSelectedBtn = document.querySelector(`#transactions-${accountId} .categorize-selected-btn`);
    
    if (aiSuggestBtn) aiSuggestBtn.disabled = selectedCount === 0;
    if (categorizeSelectedBtn) categorizeSelectedBtn.disabled = selectedCount === 0;
}

function getSelectedTransactionIds(accountId) {
    const container = document.getElementById(`transactions-${accountId}`);
    if (!container) return [];
    
    return Array.from(container.querySelectorAll('.transaction-checkbox:checked'))
        .map(checkbox => checkbox.value);
}

function handleAddTransaction(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        Saving...
    `;
    
    // Submit data to API
    fetch('/api/add-transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('addTransactionModal')).hide();
            
            // Show success message
            showAlert('Transaction added successfully', 'success');
            
            // Reload transactions for the affected account
            const accountId = document.getElementById('transaction_account_id').value;
            const transactionsContainer = document.getElementById(`transactions-${accountId}`);
            
            if (transactionsContainer) {
                transactionsContainer.innerHTML = `
                    <div class="text-center py-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Refreshing transactions...</p>
                    </div>
                `;
                
                // Fetch fresh data
                fetchAccountTransactions(accountId)
                    .then(transactions => {
                        renderTransactions(accountId, transactions);
                    });
            }
        } else {
            showAlert(data.message || 'Error adding transaction', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'error');
    })
    .finally(() => {
        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    });
}

function updateTransactionCategory(transactionId, categoryId, saveBtn) {
    // Show loading state
    const originalBtnHtml = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i data-feather="loader" class="rotate"></i>';
    feather.replace();
    
    const data = {
        transaction_id: transactionId,
        category_id: categoryId
    };
    
    fetch('/api/update-category', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            saveBtn.classList.remove('btn-warning');
            saveBtn.classList.add('btn-outline-primary');
            saveBtn.innerHTML = '<i data-feather="check"></i>';
            setTimeout(() => {
                saveBtn.innerHTML = originalBtnHtml;
                feather.replace();
            }, 2000);
            
            showAlert('Category updated successfully', 'success');
        } else {
            saveBtn.innerHTML = '<i data-feather="alert-circle"></i>';
            showAlert(data.message || 'Failed to update category', 'error');
            
            setTimeout(() => {
                saveBtn.innerHTML = originalBtnHtml;
                feather.replace();
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        saveBtn.innerHTML = '<i data-feather="alert-circle"></i>';
        showAlert('Network error occurred', 'error');
        
        setTimeout(() => {
            saveBtn.innerHTML = originalBtnHtml;
            feather.replace();
        }, 2000);
    })
    .finally(() => {
        saveBtn.disabled = false;
        feather.replace();
    });
}

function editTransaction(transactionId) {
    // This would normally fetch the transaction details from the server
    // For now, we'll use the data available in the DOM
    const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
    if (!row) return;
    
    const date = row.querySelector('td:nth-child(2)').textContent;
    const description = row.querySelector('.transaction-description').textContent;
    const fullDescription = row.querySelector('.full-description');
    const amount = row.querySelector('td:nth-child(4) span').textContent
        .replace(/[+\-$]/g, ''); // Remove +, -, and $ symbols
    const isExpense = row.querySelector('td:nth-child(4) span').classList.contains('text-danger');
    const categorySelect = row.querySelector('.category-select');
    const categoryId = categorySelect ? categorySelect.value : '';
    
    // Populate the form
    const form = document.getElementById('add-transaction-form');
    form.reset();
    
    // Convert date string to Date object
    const dateObj = new Date(date);
    document.getElementById('transaction_date').valueAsDate = dateObj;
    
    document.getElementById('transaction_description').value = fullDescription ? fullDescription.textContent : description;
    document.getElementById('transaction_amount').value = amount;
    document.getElementById('transaction_type').value = isExpense ? 'expense' : 'income';
    document.getElementById('transaction_category').value = categoryId;
    
    // We'll need to add a hidden field for the transaction ID
    let transactionIdInput = document.getElementById('edit_transaction_id');
    if (!transactionIdInput) {
        transactionIdInput = document.createElement('input');
        transactionIdInput.type = 'hidden';
        transactionIdInput.id = 'edit_transaction_id';
        transactionIdInput.name = 'transaction_id';
        form.appendChild(transactionIdInput);
    }
    transactionIdInput.value = transactionId;
    
    // Change the modal title and button text
    document.querySelector('#addTransactionModal .modal-title').innerHTML = '<i data-feather="edit-2"></i> Edit Transaction';
    document.querySelector('#addTransactionModal button[type="submit"]').innerHTML = '<i data-feather="save"></i> Update Transaction';
    
    // Show the modal
    new bootstrap.Modal(document.getElementById('addTransactionModal')).show();
    
    // Update feather icons
    feather.replace();
}

function deleteTransaction(transactionId) {
    if (confirm('Are you sure you want to delete this transaction? This cannot be undone.')) {
        fetch('/api/delete-transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transaction_id: transactionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the row from the DOM
                const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
                if (row) {
                    row.remove();
                }
                
                showAlert('Transaction deleted successfully', 'success');
                
                // Update counts
                const accountId = row.closest('.transactions-container').id.replace('transactions-', '');
                if (accountId) {
                    updateSelectedCount(accountId);
                }
            } else {
                showAlert(data.message || 'Failed to delete transaction', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Network error occurred', 'error');
        });
    }
}

function showBulkCategorizeModal(transactionIds = null) {
    const selectedIds = transactionIds || Array.from(selectedTransactions);
    const count = selectedIds.length;
    
    if (count === 0) {
        showAlert('Please select transactions to categorize', 'warning');
        return;
    }
    
    // Update count in modal title
    document.getElementById('bulk-selected-count').textContent = count;
    
    // Update global selectedTransactions if transactionIds were passed
    if (transactionIds) {
        selectedTransactions.clear();
        transactionIds.forEach(id => selectedTransactions.add(id.toString()));
    }
    
    // Load quick categories for the modal
    loadQuickCategoriesForBulkModal();
    
    // Load and display selected transactions preview
    loadSelectedTransactionsPreview();
    
    // Reset category selection
    document.getElementById('bulk_category').value = '';
    document.getElementById('confirm-bulk-categorize').disabled = true;
    
    // Show modal
    new bootstrap.Modal(document.getElementById('bulkCategorizeModal')).show();
}

function handleBulkCategorize() {
    const transactionIds = Array.from(selectedTransactions);
    const categoryId = document.getElementById('bulk_category').value;
    
    if (!categoryId) {
        showAlert('Please select a category', 'warning');
        return;
    }
    
    if (transactionIds.length === 0) {
        showAlert('No transactions selected', 'warning');
        return;
    }
    
    // Show loading state
    const button = document.getElementById('confirm-bulk-categorize');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Processing...';
    
    // Send request to API
    fetch('/api/bulk-categorize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            transaction_ids: transactionIds,
            category_id: categoryId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('bulkCategorizeModal')).hide();
            
            // Show success message
            showAlert(`Successfully categorized ${transactionIds.length} transactions`, 'success');
            
            // Update UI - change category in all affected rows
            transactionIds.forEach(id => {
                const select = document.querySelector(`.category-select[data-transaction-id="${id}"]`);
                if (select) {
                    select.value = categoryId;
                    
                    // Reset the save button
                    const saveBtn = document.querySelector(`.save-category[data-transaction-id="${id}"]`);
                    if (saveBtn) {
                        saveBtn.classList.remove('btn-warning');
                        saveBtn.classList.add('btn-outline-primary');
                        saveBtn.innerHTML = '<i data-feather="save"></i>';
                    }
                }
            });
            
            // Clear selections
            clearSelections();
            
            // Update feather icons
            feather.replace();
        } else {
            showAlert(data.message || 'Failed to categorize transactions', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'error');
    })
    .finally(() => {
        // Restore button
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

function clearSelections() {
    // Clear global set of selected transactions
    selectedTransactions.clear();
    
    // Uncheck all checkboxes
    document.querySelectorAll('.transaction-checkbox, .select-all-transactions').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Update all selected counts
    document.querySelectorAll('.account-item').forEach(item => {
        const accountId = item.dataset.accountId;
        updateSelectedCount(accountId);
    });
}

function requestAiSuggestions(transactionIds) {
    if (transactionIds.length === 0) {
        showAlert('Please select transactions to get AI suggestions', 'warning');
        return;
    }
    
    // Show the modal with loading state
    document.getElementById('ai-suggestions-container').innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Generating AI suggestions...</p>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('aiSuggestionsModal'));
    modal.show();
    
    // Make API request
    fetch('/api/ai-suggest-categories', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ transaction_ids: transactionIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderAiSuggestions(data.suggestions);
        } else {
            document.getElementById('ai-suggestions-container').innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle"></i>
                    ${data.message || 'Error getting AI suggestions'}
                </div>
            `;
            feather.replace();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('ai-suggestions-container').innerHTML = `
            <div class="alert alert-danger">
                <i data-feather="alert-circle"></i>
                Network error occurred
            </div>
        `;
        feather.replace();
    });
}

function renderAiSuggestions(suggestions) {
    if (!suggestions || Object.keys(suggestions).length === 0) {
        document.getElementById('ai-suggestions-container').innerHTML = `
            <div class="alert alert-info">
                <i data-feather="info"></i>
                No suggestions available for the selected transactions
            </div>
        `;
        feather.replace();
        return;
    }
    
    let html = `
        <div class="mb-3">
            <div class="alert alert-info">
                <i data-feather="info"></i>
                AI has provided category suggestions for ${Object.keys(suggestions).length} transactions.
                Check the ones you'd like to apply.
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th style="width: 40px;">
                            <input type="checkbox" class="form-check-input" id="select-all-suggestions" checked>
                        </th>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Suggested Category</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    Object.entries(suggestions).forEach(([transactionId, data]) => {
        html += `
            <tr data-transaction-id="${transactionId}">
                <td>
                    <input type="checkbox" class="form-check-input suggestion-checkbox" 
                           id="suggestion-${transactionId}" 
                           data-transaction-id="${transactionId}" 
                           checked>
                </td>
                <td>${new Date(data.date).toLocaleDateString()}</td>
                <td>
                    <div class="fw-semibold">${data.description.substring(0, 50)}${data.description.length > 50 ? '...' : ''}</div>
                    ${data.merchant ? `<small class="text-muted">${data.merchant}</small>` : ''}
                </td>
                <td>
                    <span class="fw-bold text-${data.amount < 0 ? 'danger' : 'success'}">
                        ${data.amount < 0 ? '-' : '+'}$${Math.abs(parseFloat(data.amount)).toFixed(2)}
                    </span>
                </td>
                <td>
                    <select class="form-select form-select-sm suggestion-category" data-transaction-id="${transactionId}">
                        <option value="">Uncategorized</option>
                        ${renderCategoryOptions(data.category_id)}
                    </select>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('ai-suggestions-container').innerHTML = html;
    
    // Add event listeners
    document.getElementById('select-all-suggestions').addEventListener('change', function() {
        const isChecked = this.checked;
        document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
            checkbox.checked = isChecked;
        });
    });
    
    feather.replace();
}

function acceptAllSuggestions() {
    document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
        checkbox.checked = true;
    });
}

function applySelectedSuggestions() {
    const suggestions = [];
    
    document.querySelectorAll('.suggestion-checkbox:checked').forEach(checkbox => {
        const transactionId = checkbox.dataset.transactionId;
        const select = document.querySelector(`.suggestion-category[data-transaction-id="${transactionId}"]`);
        
        if (select && select.value) {
            suggestions.push({
                transaction_id: transactionId,
                category_id: select.value
            });
        }
    });
    
    if (suggestions.length === 0) {
        showAlert('No suggestions selected to apply', 'warning');
        return;
    }
    
    // Show loading state
    const button = document.getElementById('apply-suggestions');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Applying...';
    
    // Make API request
    fetch('/api/apply-suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ suggestions })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('aiSuggestionsModal')).hide();
            
            // Show success message
            showAlert(`Successfully applied ${suggestions.length} category suggestions`, 'success');
            
            // Update UI - reload all transaction lists
            loadAccountTransactions();
        } else {
            showAlert(data.message || 'Failed to apply suggestions', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'error');
    })
    .finally(() => {
        // Restore button
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after a few seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 4000);
}

// Enhanced Categorization Functions

function loadCategoryOverview() {
    fetch('/api/category-overview')
        .then(response => response.json())
        .then(data => {
            renderCategoryOverview(data.categories || []);
        })
        .catch(error => {
            console.error('Error loading category overview:', error);
        });
}

function renderCategoryOverview(categories) {
    const container = document.getElementById('category-overview');
    
    let html = '';
    categories.forEach(category => {
        const percentage = category.total_transactions > 0 ? 
            ((category.transaction_count / category.total_transactions) * 100).toFixed(1) : 0;
        
        html += `
            <div class="col-md-3 col-sm-6">
                <div class="card category-card h-100" data-category-id="${category.id}">
                    <div class="card-body text-center">
                        <div class="d-flex align-items-center justify-content-center mb-2">
                            <div class="category-color-dot me-2" style="background-color: ${category.color}; width: 12px; height: 12px; border-radius: 50%;"></div>
                            <h6 class="card-title mb-0 text-truncate">${category.name}</h6>
                        </div>
                        <div class="mb-2">
                            <h4 class="text-primary mb-0">${category.transaction_count}</h4>
                            <small class="text-muted">transactions</small>
                        </div>
                        <div class="mb-2">
                            <strong class="${category.total_amount >= 0 ? 'text-success' : 'text-danger'}">
                                ${category.total_amount >= 0 ? '+' : ''}$${Math.abs(category.total_amount).toFixed(2)}
                            </strong>
                        </div>
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar" style="width: ${percentage}%; background-color: ${category.color};"></div>
                        </div>
                        <small class="text-muted">${percentage}% of transactions</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add click listeners to category cards
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const categoryId = this.dataset.categoryId;
            filterByCategory(categoryId);
        });
    });
}

function loadUncategorizedSummary() {
    fetch('/api/uncategorized-summary')
        .then(response => response.json())
        .then(data => {
            const uncategorizedCount = data.count || 0;
            const uncategorizedAmount = data.total_amount || 0;
            
            document.getElementById('uncategorized-count').textContent = uncategorizedCount;
            document.getElementById('uncategorized-amount').textContent = `$${Math.abs(uncategorizedAmount).toFixed(2)}`;
            
            if (uncategorizedCount > 0) {
                document.getElementById('uncategorized-summary').style.display = 'block';
            } else {
                document.getElementById('uncategorized-summary').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading uncategorized summary:', error);
        });
}

function openQuickCategorizePanel() {
    // Load uncategorized transactions for quick categorization
    loadQuickCategorizeData();
    
    // Show the offcanvas panel
    const offcanvas = new bootstrap.Offcanvas(document.getElementById('quickCategorizePanel'));
    offcanvas.show();
}

function loadQuickCategorizeData() {
    // Load categories for quick categorization
    fetch('/api/categories')
        .then(response => response.json())
        .then(data => {
            renderQuickCategorizeCategories(data.categories || []);
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
    
    // Load uncategorized transactions
    fetch('/api/uncategorized-transactions')
        .then(response => response.json())
        .then(data => {
            renderQuickCategorizeTransactions(data.transactions || []);
        })
        .catch(error => {
            console.error('Error loading uncategorized transactions:', error);
        });
}

function renderQuickCategorizeCategories(categories) {
    const container = document.getElementById('quick-categorize-categories');
    
    let html = '';
    categories.forEach(category => {
        html += `
            <button class="btn btn-outline-primary btn-sm quick-cat-btn" data-category-id="${category.id}">
                <div class="d-flex align-items-center">
                    <div class="category-color-dot me-2" style="background-color: ${category.color}; width: 8px; height: 8px; border-radius: 50%;"></div>
                    ${category.name}
                </div>
            </button>
        `;
    });
    
    container.innerHTML = html;
    
    // Add click listeners
    document.querySelectorAll('.quick-cat-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            selectQuickCategory(this.dataset.categoryId, this.textContent.trim());
        });
    });
}

function renderQuickCategorizeTransactions(transactions) {
    const container = document.getElementById('quick-categorize-transactions');
    
    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <i data-feather="check-circle" class="text-success mb-2"></i>
                <p class="text-muted">All transactions are categorized!</p>
            </div>
        `;
        feather.replace();
        return;
    }
    
    let html = '';
    transactions.forEach(transaction => {
        const amountClass = transaction.transaction_type === 'expense' ? 'text-danger' : 'text-success';
        const amountPrefix = transaction.transaction_type === 'expense' ? '-' : '+';
        
        html += `
            <div class="card mb-2 quick-transaction" data-transaction-id="${transaction.id}">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 text-truncate">${transaction.description}</h6>
                            <small class="text-muted">${new Date(transaction.date).toLocaleDateString()}</small>
                        </div>
                        <div class="text-end">
                            <strong class="${amountClass}">${amountPrefix}$${Math.abs(transaction.amount).toFixed(2)}</strong>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add click listeners to transactions
    document.querySelectorAll('.quick-transaction').forEach(card => {
        card.addEventListener('click', function() {
            selectQuickTransaction(this);
        });
    });
}

let selectedQuickTransaction = null;
let selectedQuickCategory = null;

function selectQuickTransaction(transactionElement) {
    // Remove previous selection
    document.querySelectorAll('.quick-transaction').forEach(el => {
        el.classList.remove('border-primary');
    });
    
    // Select new transaction
    transactionElement.classList.add('border-primary');
    selectedQuickTransaction = transactionElement.dataset.transactionId;
    
    // If category is selected, enable quick categorization
    if (selectedQuickCategory) {
        performQuickCategorization();
    }
}

function selectQuickCategory(categoryId, categoryName) {
    // Remove previous selection
    document.querySelectorAll('.quick-cat-btn').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    // Select new category
    event.target.closest('.quick-cat-btn').classList.remove('btn-outline-primary');
    event.target.closest('.quick-cat-btn').classList.add('btn-primary');
    selectedQuickCategory = categoryId;
    
    // If transaction is selected, enable quick categorization
    if (selectedQuickTransaction) {
        performQuickCategorization();
    }
}

function performQuickCategorization() {
    if (!selectedQuickTransaction || !selectedQuickCategory) return;
    
    fetch('/api/categorize-transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            transaction_id: selectedQuickTransaction,
            category_id: selectedQuickCategory
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the categorized transaction from the list
            const transactionElement = document.querySelector(`[data-transaction-id="${selectedQuickTransaction}"]`);
            if (transactionElement) {
                transactionElement.remove();
            }
            
            // Reset selections
            selectedQuickTransaction = null;
            selectedQuickCategory = null;
            
            // Remove category selection
            document.querySelectorAll('.quick-cat-btn').forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            });
            
            // Refresh data
            loadUncategorizedSummary();
            loadCategoryOverview();
            
            showAlert('Transaction categorized successfully!', 'success');
        } else {
            showAlert(data.message || 'Failed to categorize transaction', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'error');
    });
}

function autoCategorizeTranactions() {
    // Show confirmation
    if (!confirm('This will use AI to automatically categorize all uncategorized transactions. Continue?')) {
        return;
    }
    
    const button = document.getElementById('ai-auto-categorize');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> AI Processing...';
    
    fetch('/api/ai-auto-categorize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Successfully categorized ${data.categorized_count} transactions!`, 'success');
            
            // Refresh data
            loadUncategorizedSummary();
            loadCategoryOverview();
            loadAccountTransactions();
        } else {
            showAlert(data.message || 'Failed to auto-categorize transactions', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'error');
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

function categorizeAllUncategorized() {
    // Fetch all uncategorized transactions and open bulk categorize modal
    fetch('/api/uncategorized-transactions')
        .then(response => response.json())
        .then(data => {
            if (data.transactions && data.transactions.length > 0) {
                // Select all uncategorized transactions
                selectedTransactions.clear();
                data.transactions.forEach(transaction => {
                    selectedTransactions.add(transaction.id.toString());
                });
                
                showBulkCategorizeModal();
            } else {
                showAlert('No uncategorized transactions found', 'info');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to load uncategorized transactions', 'error');
        });
}

function filterByCategory(categoryId) {
    // Set the category filter and apply
    document.getElementById('transaction-category-filter').value = categoryId;
    applyFilters();
}

function loadQuickCategoriesForBulkModal() {
    fetch('/api/categories')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('quick-category-grid');
            let html = '';
            
            // Show most used categories first
            const categories = (data.categories || []).slice(0, 8); // Show top 8 categories
            categories.forEach(category => {
                html += `
                    <div class="col-md-3 col-sm-6">
                        <button class="btn btn-outline-secondary w-100 quick-bulk-category" data-category-id="${category.id}">
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="category-color-dot me-2" style="background-color: ${category.color}; width: 8px; height: 8px; border-radius: 50%;"></div>
                                <small>${category.name}</small>
                            </div>
                        </button>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            
            // Add click listeners to quick category buttons
            document.querySelectorAll('.quick-bulk-category').forEach(btn => {
                btn.addEventListener('click', function() {
                    // Update dropdown selection
                    document.getElementById('bulk_category').value = this.dataset.categoryId;
                    
                    // Update visual selection
                    document.querySelectorAll('.quick-bulk-category').forEach(b => {
                        b.classList.remove('btn-primary');
                        b.classList.add('btn-outline-secondary');
                    });
                    this.classList.remove('btn-outline-secondary');
                    this.classList.add('btn-primary');
                    
                    // Enable categorize button
                    document.getElementById('confirm-bulk-categorize').disabled = false;
                });
            });
            
            // Also listen to the dropdown changes
            document.getElementById('bulk_category').addEventListener('change', function() {
                const selectedCategoryId = this.value;
                
                // Update quick category button selection
                document.querySelectorAll('.quick-bulk-category').forEach(btn => {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-secondary');
                    
                    if (btn.dataset.categoryId === selectedCategoryId) {
                        btn.classList.remove('btn-outline-secondary');
                        btn.classList.add('btn-primary');
                    }
                });
                
                // Enable/disable categorize button
                document.getElementById('confirm-bulk-categorize').disabled = !selectedCategoryId;
            });
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

function loadSelectedTransactionsPreview() {
    const transactionIds = Array.from(selectedTransactions);
    const container = document.getElementById('selected-transactions-preview');
    
    // Get transaction details from the DOM (simplified preview)
    let html = '';
    let totalAmount = 0;
    
    transactionIds.forEach(transactionId => {
        const transactionRow = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (transactionRow) {
            const description = transactionRow.querySelector('td:nth-child(3)').textContent.trim();
            const amountText = transactionRow.querySelector('td:nth-child(4)').textContent.trim();
            const amount = parseFloat(amountText.replace(/[^0-9.-]/g, ''));
            totalAmount += Math.abs(amount);
            
            html += `
                <div class="d-flex justify-content-between align-items-center py-1 border-bottom">
                    <span class="text-truncate">${description}</span>
                    <small class="text-muted">${amountText}</small>
                </div>
            `;
        }
    });
    
    html += `
        <div class="d-flex justify-content-between align-items-center py-2 mt-2 bg-light rounded">
            <strong>Total: ${transactionIds.length} transactions</strong>
            <strong>$${totalAmount.toFixed(2)}</strong>
        </div>
    `;
    
    container.innerHTML = html;
} 