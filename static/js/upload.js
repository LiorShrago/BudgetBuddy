// CSV Upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const submitButton = uploadForm.querySelector('button[type="submit"]');
    
    // File input change handler
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            validateFile(file);
        }
    });
    
    // Form submission handler
    uploadForm.addEventListener('submit', function(e) {
        const file = fileInput.files[0];
        const accountId = document.getElementById('account_id').value;
        
        if (!file || !accountId) {
            e.preventDefault();
            showAlert('Please select both a file and an account.', 'error');
            return;
        }
        
        if (!validateFile(file)) {
            e.preventDefault();
            return;
        }
        
        // Show loading state
        setLoadingState(true);
    });
    
    // Drag and drop functionality
    const uploadArea = document.createElement('div');
    uploadArea.className = 'upload-area mt-3';
    uploadArea.innerHTML = `
        <i data-feather="upload-cloud" style="width: 48px; height: 48px;" class="text-muted mb-2"></i>
        <p class="mb-0">Drag and drop your CSV file here, or click to browse</p>
    `;
    
    // Insert upload area after file input
    fileInput.parentNode.insertBefore(uploadArea, fileInput.nextSibling);
    
    // Hide default file input
    fileInput.style.display = 'none';
    
    // Click to browse
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    });
    
    // Update feather icons
    feather.replace();
});

function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel'];
    
    // Check file type
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv')) {
        showAlert('Please select a valid CSV file.', 'error');
        return false;
    }
    
    // Check file size
    if (file.size > maxSize) {
        showAlert('File size must be less than 16MB.', 'error');
        return false;
    }
    
    // Show file info
    showFileInfo(file);
    return true;
}

function showFileInfo(file) {
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    const fileInfo = document.querySelector('.file-info');
    
    if (fileInfo) {
        fileInfo.remove();
    }
    
    const infoDiv = document.createElement('div');
    infoDiv.className = 'file-info alert alert-info mt-2';
    infoDiv.innerHTML = `
        <i data-feather="file" class="me-2"></i>
        <strong>${file.name}</strong> (${fileSize} MB)
    `;
    
    document.querySelector('.upload-area').parentNode.insertBefore(
        infoDiv, 
        document.querySelector('.upload-area').nextSibling
    );
    
    feather.replace();
}

function setLoadingState(loading) {
    const submitButton = document.querySelector('#uploadForm button[type="submit"]');
    const form = document.getElementById('uploadForm');
    
    if (loading) {
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Processing...
        `;
        form.classList.add('loading');
    } else {
        submitButton.disabled = false;
        submitButton.innerHTML = `
            <i data-feather="upload"></i>
            Upload and Process
        `;
        form.classList.remove('loading');
        feather.replace();
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// CSV preview functionality (optional enhancement)
function previewCSV(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const csv = e.target.result;
        const lines = csv.split('\n').slice(0, 5); // First 5 lines
        
        const previewDiv = document.createElement('div');
        previewDiv.className = 'csv-preview mt-3';
        previewDiv.innerHTML = `
            <h6>CSV Preview:</h6>
            <pre class="bg-dark text-light p-2 rounded">${lines.join('\n')}</pre>
        `;
        
        const existingPreview = document.querySelector('.csv-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        document.querySelector('.upload-area').parentNode.appendChild(previewDiv);
    };
    reader.readAsText(file);
}

// Export for use in other modules
window.UploadUtils = {
    validateFile,
    showFileInfo,
    setLoadingState,
    showAlert,
    previewCSV
};
