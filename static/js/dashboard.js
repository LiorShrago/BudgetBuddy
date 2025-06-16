// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize spending chart
    initializeSpendingChart();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update feather icons
    feather.replace();
});

function setupEventListeners() {
    // Time period change
    document.getElementById('dashboard-time-period').addEventListener('change', function() {
        initializeSpendingChart();
    });

    // Refresh button
    document.getElementById('refresh-dashboard-chart').addEventListener('click', function() {
        initializeSpendingChart();
    });
}

function initializeSpendingChart() {
    const ctx = document.getElementById('spendingChart');
    if (!ctx) return;
    
    // Get selected time period
    const timePeriod = document.getElementById('dashboard-time-period').value;
    
    // Fetch spending data from API with time period
    fetch(`/api/spending-chart?period=${timePeriod}`)
        .then(response => response.json())
        .then(data => {
            if (data.labels.length === 0) {
                // Show no data message
                const chartContainer = document.getElementById('dashboard-chart-container');
                const breakdownContainer = document.getElementById('dashboard-breakdown-container');
                
                chartContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i data-feather="pie-chart" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                        <h6>No Spending Data</h6>
                        <p class="text-muted">Import transactions to see breakdown.</p>
                    </div>
                `;
                
                breakdownContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i data-feather="inbox" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                        <p class="text-muted">Category breakdown will appear here</p>
                    </div>
                `;
                
                feather.replace();
                return;
            }
            
            // Create chart
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 2,
                        borderColor: '#fff',
                        hoverOffset: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false  // We'll show the legend in the breakdown list
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#fff',
                            borderWidth: 1,
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
            
            // Update breakdown list
            updateDashboardCategoryBreakdown(data);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            const chartContainer = document.getElementById('dashboard-chart-container');
            const breakdownContainer = document.getElementById('dashboard-breakdown-container');
            
            chartContainer.innerHTML = `
                <div class="text-center py-5">
                    <i data-feather="alert-circle" class="text-warning mb-3" style="width: 48px; height: 48px;"></i>
                    <h6>Error Loading Chart</h6>
                    <p class="text-muted">Unable to load spending data.</p>
                </div>
            `;
            
            breakdownContainer.innerHTML = `
                <div class="text-center py-5">
                    <i data-feather="alert-circle" class="text-warning mb-3" style="width: 48px; height: 48px;"></i>
                    <p class="text-muted">Unable to load breakdown data.</p>
                </div>
            `;
            
            feather.replace();
        });
}

function updateDashboardCategoryBreakdown(data) {
    const container = document.getElementById('dashboard-category-breakdown');
    const timePeriod = document.getElementById('dashboard-time-period').value;
    
    const total = data.data.reduce((sum, value) => sum + value, 0);
    
    const periodText = getPeriodDisplayText(timePeriod);
    
    let html = `
        <div class="breakdown-header">${periodText} Spending</div>
        <div class="breakdown-total">
            <h6>Total Expenses</h6>
            <h5>$${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h5>
        </div>
    `;

    data.labels.forEach((label, index) => {
        const value = data.data[index];
        const percentage = ((value / total) * 100).toFixed(1);
        const color = data.colors[index];

        html += `
            <div class="category-item">
                <div class="category-color" style="background-color: ${color};"></div>
                <div class="category-info">
                    <div class="category-name">${label}</div>
                    <div class="category-amount">$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    <div class="category-progress">
                        <div class="category-progress-bar" style="width: 0%; background-color: ${color};"></div>
                    </div>
                </div>
                <div class="category-percentage">${percentage}%</div>
            </div>
        `;
    });

    container.innerHTML = html;
    
    // Animate progress bars
    setTimeout(() => {
        const progressBars = container.querySelectorAll('.category-progress-bar');
        data.labels.forEach((label, index) => {
            const value = data.data[index];
            const percentage = ((value / total) * 100).toFixed(1);
            progressBars[index].style.width = percentage + '%';
        });
    }, 300);
}

function toggleDashboardView() {
    const chartContainer = document.getElementById('dashboard-chart-container');
    const breakdownContainer = document.getElementById('dashboard-breakdown-container');
    
    if (chartContainer.style.display === 'none') {
        chartContainer.style.display = 'block';
        breakdownContainer.classList.remove('col-lg-12');
        breakdownContainer.classList.add('col-lg-6');
    } else {
        chartContainer.style.display = 'none';
        breakdownContainer.classList.remove('col-lg-6');
        breakdownContainer.classList.add('col-lg-12');
    }
}

function getPeriodDisplayText(period) {
    const periodMap = {
        'week': 'This Week\'s',
        'month': 'This Month\'s',
        'year': 'This Year\'s',
        'last_30': 'Last 30 Days\'',
        'last_90': 'Last 3 Months\''
    };
    
    return periodMap[period] || 'Current';
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
