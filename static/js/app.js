// ISMS Manager - Main JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || '¿Estás seguro de que deseas eliminar este elemento?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-calculate risk level
    const probabilityInput = document.getElementById('probability');
    const impactInput = document.getElementById('impact');
    const riskLevelDisplay = document.getElementById('risk-level');

    if (probabilityInput && impactInput && riskLevelDisplay) {
        function calculateRiskLevel() {
            const probability = parseInt(probabilityInput.value) || 0;
            const impact = parseInt(impactInput.value) || 0;
            const score = probability * impact;

            let level, className;
            if (score <= 4) {
                level = 'Bajo';
                className = 'badge bg-success';
            } else if (score <= 9) {
                level = 'Medio';
                className = 'badge bg-warning';
            } else if (score <= 16) {
                level = 'Alto';
                className = 'badge bg-danger';
            } else {
                level = 'Crítico';
                className = 'badge bg-dark';
            }

            riskLevelDisplay.innerHTML = `<span class="${className}">${level} (${score})</span>`;
        }

        probabilityInput.addEventListener('change', calculateRiskLevel);
        impactInput.addEventListener('change', calculateRiskLevel);
        calculateRiskLevel(); // Initial calculation
    }

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    const searchableItems = document.querySelectorAll('[data-searchable]');

    if (searchInput && searchableItems.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();

            searchableItems.forEach(function(item) {
                const searchText = item.getAttribute('data-searchable').toLowerCase();
                const shouldShow = searchText.includes(searchTerm);

                if (shouldShow) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Dynamic form fields
    const addFieldButtons = document.querySelectorAll('[data-add-field]');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const templateId = this.getAttribute('data-add-field');
            const template = document.getElementById(templateId);
            const container = this.previousElementSibling;

            if (template && container) {
                const newField = template.cloneNode(true);
                newField.style.display = 'block';
                newField.removeAttribute('id');
                container.appendChild(newField);
            }
        });
    });

    // Status update functionality
    const statusSelects = document.querySelectorAll('[data-status-update]');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const newStatus = this.value;
            const updateUrl = this.getAttribute('data-status-update');

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    id: itemId,
                    status: newStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Estado actualizado correctamente', 'success');
                } else {
                    showAlert('Error al actualizar el estado', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error de conexión', 'error');
            });
        });
    });
});

// Utility functions
function getCSRFToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || document.querySelector('main');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        if (bsAlert) {
            bsAlert.close();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}