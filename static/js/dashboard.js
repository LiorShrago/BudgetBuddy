// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize spending chart
    initializeSpendingChart();
    
    // Update feather icons
    feather.replace();
});

function initializeSpendingChart() {
    const ctx = document.getElementById('spendingChart');
    if (!ctx) return;
    
    // Fetch spending data from API
    fetch('/api/spending-chart')
        .then(response => response.json())
        .then(data => {
            if (data.labels.length === 0) {
                // Show no data message
                ctx.parentElement.innerHTML = `
                    <div class="text-center py-5">
                        <i data-feather="pie-chart" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                        <h6>No Spending Data</h6>
                        <p class="text-muted">Start importing transactions to see your spending breakdown.</p>
                    </div>
                `;
                feather.replace();
                return;
            }
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 2,
                        borderColor: 'rgba(255, 255, 255, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                color: '#ffffff'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${context.label}: $${value.toFixed(2)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            ctx.parentElement.innerHTML = `
                <div class="text-center py-5">
                    <i data-feather="alert-circle" class="text-warning mb-3" style="width: 48px; height: 48px;"></i>
                    <h6>Error Loading Chart</h6>
                    <p class="text-muted">Unable to load spending data.</p>
                </div>
            `;
            feather.replace();
        });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format percentage
function formatPercentage(value) {
    return `${value.toFixed(1)}%`;
}
