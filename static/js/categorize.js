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
        aiCategorizeAll();
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
    
    // Helper function for API requests with consistent error handling
    function makeApiRequest(url, data, successMessage, onSuccess = null) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showAlert(successMessage, 'success');
                if (onSuccess) onSuccess(result);
                setTimeout(() => window.location.reload(), 800);
            } else {
                showAlert(result.message || 'Operation failed', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Network error occurred', 'error');
        });
    }

    function bulkCategorizeTransactions(transactionIds, categoryId) {
        const data = { transaction_ids: transactionIds, category_id: categoryId };
        const successMessage = `Successfully categorized ${transactionIds.length} transactions`;
        
        makeApiRequest('/api/bulk-categorize', data, successMessage, () => {
            clearAllSelections();
            updateSelectedCount();
        });
    }
    
    function updateTransactionCategory(transactionId, categoryId, saveBtn) {
        const data = { transaction_id: transactionId, category_id: categoryId };
        makeApiRequest('/api/update-category', data, 'Category updated successfully');
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
                
                // Clear form and don't reload page
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
        aiCategorizeAllBtn.innerHTML = '<i data-feather="loader" class="rotate"></i> Getting AI suggestions...';
        aiCategorizeAllBtn.disabled = true;
        
        fetch('/api/ai-suggest-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.suggestions) {
                showAISuggestionsModal(data.suggestions);
            } else {
                showAlert(data.message || 'Error getting AI suggestions', 'error');
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
    
    function showAISuggestionsModal(suggestions) {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="aiSuggestionsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i data-feather="zap"></i>
                                AI Categorization Suggestions
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                <strong>Review AI Suggestions:</strong> You can approve, modify, or discard each suggestion below.
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Description</th>
                                            <th>Amount</th>
                                            <th>AI Suggestion</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody id="suggestions-list">
                                        ${renderSuggestionRows(suggestions)}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <div class="d-flex justify-content-between w-100">
                                <div>
                                    <button type="button" class="btn btn-outline-success" onclick="acceptAllSuggestions()">
                                        <i data-feather="check-circle"></i>
                                        Accept All
                                    </button>
                                    <button type="button" class="btn btn-outline-danger" onclick="discardAllSuggestions()">
                                        <i data-feather="x-circle"></i>
                                        Discard All
                                    </button>
                                </div>
                                <div>
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-primary" onclick="applySelectedSuggestions()">
                                        <i data-feather="save"></i>
                                        Apply Selected
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if present
        const existingModal = document.getElementById('aiSuggestionsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('aiSuggestionsModal'));
        modal.show();
        
        // Replace feather icons
        feather.replace();
    }
    
    function renderSuggestionRows(suggestions) {
        return suggestions.map(suggestion => `
            <tr data-transaction-id="${suggestion.transaction_id}">
                <td>${suggestion.date}</td>
                <td>
                    <div class="fw-semibold">${suggestion.description}</div>
                    ${suggestion.merchant ? `<small class="text-muted">${suggestion.merchant}</small>` : ''}
                </td>
                <td>
                    <span class="badge bg-${suggestion.amount >= 0 ? 'success' : 'danger'}">
                        $${Math.abs(suggestion.amount).toFixed(2)}
                    </span>
                </td>
                <td>
                    <select class="form-select form-select-sm suggestion-category" data-transaction-id="${suggestion.transaction_id}">
                        <option value="">Uncategorized</option>
                        ${renderCategoryOptions(suggestion.suggested_category_id)}
                    </select>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <input type="checkbox" class="btn-check suggestion-checkbox" 
                               id="suggestion-${suggestion.transaction_id}" 
                               data-transaction-id="${suggestion.transaction_id}" 
                               ${suggestion.suggested_category_id ? 'checked' : ''}>
                        <label class="btn btn-outline-success btn-sm" for="suggestion-${suggestion.transaction_id}">
                            <i data-feather="check"></i>
                        </label>
                        <button type="button" class="btn btn-outline-danger btn-sm" 
                                onclick="discardSuggestion(${suggestion.transaction_id})">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    function renderCategoryOptions(selectedCategoryId) {
        const categorySelects = document.querySelectorAll('.category-select');
        if (categorySelects.length > 0) {
            const firstSelect = categorySelects[0];
            const options = Array.from(firstSelect.querySelectorAll('option')).map(option => {
                const selected = option.value == selectedCategoryId ? 'selected' : '';
                return `<option value="${option.value}" ${selected}>${option.textContent}</option>`;
            }).join('');
            return options;
        }
        return '';
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

// Global functions for AI suggestions modal
window.acceptAllSuggestions = function() {
    document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
        checkbox.checked = true;
    });
};

window.discardAllSuggestions = function() {
    document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
};

window.discardSuggestion = function(transactionId) {
    const checkbox = document.querySelector(`#suggestion-${transactionId}`);
    if (checkbox) {
        checkbox.checked = false;
    }
};

window.applySelectedSuggestions = function() {
    const selectedSuggestions = [];
    document.querySelectorAll('.suggestion-checkbox:checked').forEach(checkbox => {
        const transactionId = checkbox.dataset.transactionId;
        const categorySelect = document.querySelector(`.suggestion-category[data-transaction-id="${transactionId}"]`);
        const categoryId = categorySelect.value;
        
        if (categoryId) {
            selectedSuggestions.push({
                transaction_id: transactionId,
                category_id: categoryId
            });
        }
    });
    
    if (selectedSuggestions.length === 0) {
        alert('No suggestions selected to apply');
        return;
    }
    
    // Apply the suggestions
    fetch('/api/apply-suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suggestions: selectedSuggestions })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide modal first
            const modalElement = document.getElementById('aiSuggestionsModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
            // Show success message and refresh page
            alert(`Successfully applied ${data.count} categorizations`);
            window.location.reload();
        } else {
            alert(data.message || 'Error applying suggestions');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error applying suggestions');
    });
};