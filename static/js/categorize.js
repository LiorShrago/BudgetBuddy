// Transaction categorization functionality
document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('select-all');
    const selectAllHeaderCheckbox = document.getElementById('select-all-header');
    const transactionCheckboxes = document.querySelectorAll('.transaction-checkbox');
    const categorizeSelectedBtn = document.getElementById('categorize-selected');
    const aiCategorizeAllBtn = document.getElementById('ai-categorize-all');
    const aiSuggestSelectedBtn = document.getElementById('ai-suggest-selected');
    const bulkCategorySelect = document.getElementById('bulk-category');
    const selectedCountBadge = document.getElementById('selected-count');
    const newCategoryForm = document.getElementById('new-category-form');
    const newCategoryModal = new bootstrap.Modal(document.getElementById('newCategoryModal'));
    
    // Initialize
    updateSelectedCount();
    
    // Select all functionality
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        transactionCheckboxes.forEach(checkbox => {
            if (!checkbox.closest('tr').style.display || checkbox.closest('tr').style.display !== 'none') {
                checkbox.checked = isChecked;
            }
        });
        selectAllHeaderCheckbox.checked = isChecked;
        updateSelectedCount();
    });
    
    selectAllHeaderCheckbox.addEventListener('change', function() {
        selectAllCheckbox.checked = this.checked;
        selectAllCheckbox.dispatchEvent(new Event('change'));
    });
    
    // Individual checkbox change
    transactionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
    
    // Bulk categorize selected transactions
    categorizeSelectedBtn.addEventListener('click', function() {
        const selectedTransactions = getSelectedTransactionIds();
        const categoryId = bulkCategorySelect.value;
        
        if (selectedTransactions.length === 0) {
            showAlert('Please select transactions to categorize', 'warning');
            return;
        }
        
        if (!categoryId) {
            showAlert('Please select a category', 'warning');
            return;
        }
        
        bulkCategorizeTransactions(selectedTransactions, categoryId);
    });
    
    // AI Auto-categorize all transactions
    aiCategorizeAllBtn.addEventListener('click', function() {
        if (confirm('This will automatically categorize all uncategorized transactions using AI. Continue?')) {
            aiCategorizeAll();
        }
    });
    
    // AI suggest categories for selected transactions
    aiSuggestSelectedBtn.addEventListener('click', function() {
        const selectedTransactions = getSelectedTransactionIds();
        
        if (selectedTransactions.length === 0) {
            showAlert('Please select transactions to get AI suggestions', 'warning');
            return;
        }
        
        aiSuggestCategories(selectedTransactions);
    });
    
    // Individual category change
    document.querySelectorAll('.category-select').forEach(select => {
        select.addEventListener('change', function() {
            const saveBtn = document.querySelector(`.save-category[data-transaction-id="${this.dataset.transactionId}"]`);
            saveBtn.classList.remove('btn-outline-primary');
            saveBtn.classList.add('btn-warning');
            saveBtn.innerHTML = '<i data-feather="clock"></i>';
            feather.replace();
        });
    });
    
    // Save individual category
    document.querySelectorAll('.save-category').forEach(btn => {
        btn.addEventListener('click', function() {
            const transactionId = this.dataset.transactionId;
            const categorySelect = document.querySelector(`.category-select[data-transaction-id="${transactionId}"]`);
            const categoryId = categorySelect.value;
            
            updateTransactionCategory(transactionId, categoryId, this);
        });
    });
    
    // Filter functionality
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    
    // New category form submission
    newCategoryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        createNewCategory();
    });
    
    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('.transaction-checkbox:checked');
        const count = checkedBoxes.length;
        selectedCountBadge.textContent = `${count} selected`;
        categorizeSelectedBtn.disabled = count === 0;
        aiSuggestSelectedBtn.disabled = count === 0;
        
        // Update select all checkbox state
        const visibleCheckboxes = Array.from(transactionCheckboxes).filter(cb => 
            !cb.closest('tr').style.display || cb.closest('tr').style.display !== 'none'
        );
        const checkedVisibleBoxes = visibleCheckboxes.filter(cb => cb.checked);
        
        if (checkedVisibleBoxes.length === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
            selectAllHeaderCheckbox.indeterminate = false;
            selectAllHeaderCheckbox.checked = false;
        } else if (checkedVisibleBoxes.length === visibleCheckboxes.length) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
            selectAllHeaderCheckbox.indeterminate = false;
            selectAllHeaderCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
            selectAllHeaderCheckbox.indeterminate = true;
        }
    }
    
    function getSelectedTransactionIds() {
        return Array.from(document.querySelectorAll('.transaction-checkbox:checked'))
            .map(checkbox => checkbox.value);
    }
    
    function bulkCategorizeTransactions(transactionIds, categoryId) {
        const data = {
            transaction_ids: transactionIds,
            category_id: categoryId
        };
        
        fetch('/api/bulk-categorize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Successfully categorized ${data.count} transactions`, 'success');
                // Update the UI
                transactionIds.forEach(transactionId => {
                    const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
                    const categorySelect = row.querySelector('.category-select');
                    categorySelect.value = categoryId;
                    
                    const saveBtn = row.querySelector('.save-category');
                    saveBtn.classList.remove('btn-warning');
                    saveBtn.classList.add('btn-outline-primary');
                    saveBtn.innerHTML = '<i data-feather="save"></i>';
                });
                feather.replace();
                
                // Clear selections
                clearAllSelections();
            } else {
                showAlert(data.message || 'Error categorizing transactions', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error categorizing transactions', 'error');
        });
    }
    
    function updateTransactionCategory(transactionId, categoryId, saveBtn) {
        const data = {
            transaction_id: transactionId,
            category_id: categoryId
        };
        
        fetch('/api/update-category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                saveBtn.classList.remove('btn-warning');
                saveBtn.classList.add('btn-outline-primary');
                saveBtn.innerHTML = '<i data-feather="save"></i>';
                feather.replace();
                showAlert('Category updated successfully', 'success');
            } else {
                showAlert(data.message || 'Error updating category', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error updating category', 'error');
        });
    }
    
    function applyFilters() {
        const categoryFilter = document.getElementById('filter-category').value;
        const accountFilter = document.getElementById('filter-account').value;
        const dateFromFilter = document.getElementById('filter-date-from').value;
        const dateToFilter = document.getElementById('filter-date-to').value;
        
        const params = new URLSearchParams();
        if (categoryFilter && categoryFilter !== 'all') params.append('category', categoryFilter);
        if (accountFilter) params.append('account', accountFilter);
        if (dateFromFilter) params.append('date_from', dateFromFilter);
        if (dateToFilter) params.append('date_to', dateToFilter);
        
        window.location.href = `/categorize?${params.toString()}`;
    }
    
    function createNewCategory() {
        const name = document.getElementById('new-category-name').value;
        const parentId = document.getElementById('new-category-parent').value;
        const color = document.getElementById('new-category-color').value;
        
        const data = {
            name: name,
            parent_id: parentId || null,
            color: color
        };
        
        fetch('/api/create-category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Category created successfully', 'success');
                newCategoryModal.hide();
                
                // Add new category to all select elements
                const newOption = `<option value="${data.category.id}">${data.category.name}</option>`;
                document.querySelectorAll('select').forEach(select => {
                    if (select.classList.contains('category-select') || 
                        select.id === 'bulk-category' || 
                        select.id === 'filter-category') {
                        select.insertAdjacentHTML('beforeend', newOption);
                    }
                });
                
                // Clear form
                newCategoryForm.reset();
            } else {
                showAlert(data.message || 'Error creating category', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error creating category', 'error');
        });
    }
    
    function clearAllSelections() {
        transactionCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        selectAllCheckbox.checked = false;
        selectAllHeaderCheckbox.checked = false;
        bulkCategorySelect.value = '';
        updateSelectedCount();
    }
    
    function aiCategorizeAll() {
        // Show loading state
        const originalText = aiCategorizeAllBtn.innerHTML;
        aiCategorizeAllBtn.innerHTML = '<i data-feather="loader" class="rotate"></i> Processing...';
        aiCategorizeAllBtn.disabled = true;
        
        fetch('/api/ai-categorize-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                // Refresh page to show updated categorizations
                setTimeout(() => window.location.reload(), 2000);
            } else {
                showAlert(data.message || 'Error in AI categorization', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error in AI categorization', 'error');
        })
        .finally(() => {
            aiCategorizeAllBtn.innerHTML = originalText;
            aiCategorizeAllBtn.disabled = false;
            feather.replace();
        });
    }
    
    function aiSuggestCategories(transactionIds) {
        // Show loading state
        const originalText = aiSuggestSelectedBtn.innerHTML;
        aiSuggestSelectedBtn.innerHTML = '<i data-feather="loader" class="rotate"></i> Getting AI suggestions...';
        aiSuggestSelectedBtn.disabled = true;
        
        const data = {
            transaction_ids: transactionIds
        };
        
        fetch('/api/ai-suggest-categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                applySuggestions(data.suggestions);
                showAlert(`AI provided suggestions for ${Object.keys(data.suggestions).length} transactions`, 'info');
            } else {
                showAlert(data.message || 'Error getting AI suggestions', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error getting AI suggestions', 'error');
        })
        .finally(() => {
            aiSuggestSelectedBtn.innerHTML = originalText;
            aiSuggestSelectedBtn.disabled = false;
            feather.replace();
        });
    }
    
    function applySuggestions(suggestions) {
        Object.keys(suggestions).forEach(transactionId => {
            const suggestion = suggestions[transactionId];
            const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
            
            if (row && suggestion.category_id) {
                const categorySelect = row.querySelector('.category-select');
                categorySelect.value = suggestion.category_id;
                
                // Highlight the suggested category
                categorySelect.style.backgroundColor = '#fff3cd';
                categorySelect.style.borderColor = '#ffc107';
                
                // Add a suggestion indicator
                const saveBtn = row.querySelector('.save-category');
                saveBtn.classList.remove('btn-outline-primary');
                saveBtn.classList.add('btn-warning');
                saveBtn.innerHTML = '<i data-feather="sun"></i>';
                saveBtn.title = `AI suggests: ${suggestion.category_name}`;
            }
        });
        
        feather.replace();
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
        
        // Auto-dismiss after 5 seconds for AI messages
        const timeout = type === 'info' ? 5000 : 3000;
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, timeout);
    }
    
    // Expand/collapse transaction descriptions
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('transaction-description')) {
            const fullDesc = e.target.parentNode.querySelector('.full-description');
            if (fullDesc) {
                if (fullDesc.classList.contains('d-none')) {
                    e.target.textContent = fullDesc.textContent;
                    fullDesc.classList.remove('d-none');
                } else {
                    e.target.textContent = fullDesc.textContent.substring(0, 50) + '...';
                    fullDesc.classList.add('d-none');
                }
            }
        }
    });
    
    // Initialize feather icons
    feather.replace();
});