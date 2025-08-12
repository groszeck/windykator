/**
 * Windykator Web - Main JavaScript File
 * Zawiera funkcje pomocnicze i obsługę interakcji
 */

// Global variables
let currentData = null;
let isProcessing = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌐 Windykator Web - JavaScript loaded');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize file drag and drop
    initializeFileDragAndDrop();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize animations
    initializeAnimations();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize file drag and drop functionality
 */
function initializeFileDragAndDrop() {
    const dropZones = document.querySelectorAll('.file-upload-area');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            zone.classList.add('dragover');
        });
        
        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            zone.classList.remove('dragover');
        });
        
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileDrop(files[0]);
            }
        });
    });
}

/**
 * Handle file drop event
 */
function handleFileDrop(file) {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.files = new DataTransfer().files;
        fileInput.dispatchEvent(new Event('change'));
    }
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                showValidationErrors(form);
            }
        });
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Show validation errors
 */
function showValidationErrors(form) {
    const invalidFields = form.querySelectorAll('.is-invalid');
    
    invalidFields.forEach(field => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = 'To pole jest wymagane';
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        field.parentNode.appendChild(errorDiv);
    });
    
    // Show alert
    showAlert('Proszę wypełnić wszystkie wymagane pola', 'warning');
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll('.card, .btn, .alert');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    animatedElements.forEach(el => observer.observe(el));
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto remove after duration
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
    
    // Add animation
    setTimeout(() => alert.classList.add('fade-in'), 100);
}

/**
 * Create alert container if it doesn't exist
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Get alert icon based on type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Show loading spinner
 */
function showLoading(element, text = 'Ładowanie...') {
    if (isProcessing) return;
    
    isProcessing = true;
    element.disabled = true;
    element.innerHTML = `
        <span class="loading-spinner me-2"></span>
        ${text}
    `;
}

/**
 * Hide loading spinner
 */
function hideLoading(element, originalText) {
    isProcessing = false;
    element.disabled = false;
    element.innerHTML = originalText;
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format date
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('pl-PL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Skopiowano do schowka', 'success', 2000);
    }).catch(() => {
        showAlert('Błąd kopiowania', 'danger', 2000);
    });
}

/**
 * Download data as CSV
 */
function downloadCSV(data, filename) {
    const csvContent = convertToCSV(data);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Convert data to CSV format
 */
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(';')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header] || '';
            return `"${value}"`;
        });
        csvRows.push(values.join(';'));
    });
    
    return csvRows.join('\n');
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local storage utilities
 */
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    }
};

/**
 * API utilities
 */
const API = {
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    get: async function(url) {
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

/**
 * Table utilities
 */
const Table = {
    sort: function(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try to parse as number
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return aNum - bNum;
            }
            
            // Sort as string
            return aValue.localeCompare(bValue, 'pl');
        });
        
        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    },
    
    filter: function(table, searchTerm) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const visible = text.includes(searchTerm.toLowerCase());
            row.style.display = visible ? '' : 'none';
        });
    }
};

// Export functions for global use
window.WindykatorWeb = {
    showAlert,
    showLoading,
    hideLoading,
    formatFileSize,
    formatDate,
    copyToClipboard,
    downloadCSV,
    Storage,
    API,
    Table
}; 