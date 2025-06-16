// Expense Visualization Dashboard
let charts = {};
let chartSettings = {
    colorScheme: 'default',
    animationStyle: 'easeOutQuart',
    showAnimations: true,
    showValues: true,
    showPercentages: true,
    darkTheme: false
};

// Color schemes
const colorSchemes = {
    default: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6B9D', '#4ECDC4'],
    pastel: ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD3BA', '#E0BBE4', '#C7CEDB', '#FEC8D8'],
    neon: ['#FF073A', '#00FFFF', '#FFFF00', '#FF00FF', '#00FF00', '#FF8C00', '#8A2BE2', '#DC143C'],
    earth: ['#8B4513', '#228B22', '#D2691E', '#CD853F', '#A0522D', '#556B2F', '#8FBC8F', '#F4A460'],
    ocean: ['#006994', '#1E90FF', '#87CEEB', '#4682B4', '#20B2AA', '#5F9EA0', '#B0E0E6', '#87CEFA'],
    sunset: ['#FF6B35', '#F7931E', '#FFD23F', '#FF8C42', '#FF5E5B', '#FFB4A2', '#F95D6A', '#FEC89A']
};

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    loadChartData();
});

function setupEventListeners() {
    // Time period change
    document.getElementById('time-period').addEventListener('change', function() {
        const customRange = document.getElementById('custom-date-range');
        if (this.value === 'custom') {
            customRange.style.display = 'block';
        } else {
            customRange.style.display = 'none';
            loadChartData();
        }
    });

    // Custom date range
    document.getElementById('start-date').addEventListener('change', loadChartData);
    document.getElementById('end-date').addEventListener('change', loadChartData);

    // Chart type change
    document.getElementById('chart-type').addEventListener('change', function() {
        updatePrimaryChart();
    });

    // Account filter
    document.getElementById('account-filter').addEventListener('change', loadChartData);

    // Refresh charts button
    document.getElementById('refresh-charts').addEventListener('click', loadChartData);

    // Export button
    document.getElementById('export-btn').addEventListener('click', exportAllCharts);

    // Customization modal
    document.getElementById('apply-customization').addEventListener('click', applyCustomization);
}

function initializeCharts() {
    // Initialize empty charts
    const primaryCtx = document.getElementById('primary-chart').getContext('2d');
    const trendCtx = document.getElementById('trend-chart').getContext('2d');
    const monthlyCtx = document.getElementById('monthly-chart').getContext('2d');
    const accountCtx = document.getElementById('account-chart').getContext('2d');

    charts.primary = new Chart(primaryCtx, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [] }] },
        options: getChartOptions('primary')
    });

    charts.trend = new Chart(trendCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [] }] },
        options: getChartOptions('trend')
    });

    charts.monthly = new Chart(monthlyCtx, {
        type: 'bar',
        data: { labels: [], datasets: [{ data: [] }] },
        options: getChartOptions('monthly')
    });

    charts.account = new Chart(accountCtx, {
        type: 'polarArea',
        data: { labels: [], datasets: [{ data: [] }] },
        options: getChartOptions('account')
    });
}

function getChartOptions(chartType) {
    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: chartSettings.showAnimations ? 1000 : 0,
            easing: chartSettings.animationStyle
        },
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    color: chartSettings.darkTheme ? '#fff' : '#333'
                }
            },
            tooltip: {
                backgroundColor: chartSettings.darkTheme ? '#333' : 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#fff',
                borderWidth: 1
            }
        }
    };

    if (chartType === 'trend' || chartType === 'monthly') {
        baseOptions.scales = {
            y: {
                beginAtZero: true,
                grid: {
                    color: chartSettings.darkTheme ? '#444' : '#e0e0e0'
                },
                ticks: {
                    color: chartSettings.darkTheme ? '#fff' : '#333',
                    callback: function(value) {
                        return '$' + value.toLocaleString();
                    }
                }
            },
            x: {
                grid: {
                    color: chartSettings.darkTheme ? '#444' : '#e0e0e0'
                },
                ticks: {
                    color: chartSettings.darkTheme ? '#fff' : '#333'
                }
            }
        };
    }

    return baseOptions;
}

function loadChartData() {
    const timePeriod = document.getElementById('time-period').value;
    const accountFilter = document.getElementById('account-filter').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    const params = new URLSearchParams({
        period: timePeriod,
        account: accountFilter || '',
        start_date: startDate || '',
        end_date: endDate || ''
    });

    fetch(`/api/visualization-data?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAllCharts(data.data);
                updateSummaryCards(data.data);
                updateFunStats(data.data);
            } else {
                showAlert('Error loading chart data', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error loading chart data', 'error');
        });
}

function updateAllCharts(data) {
    // Update primary chart (category breakdown)
    const colors = getColors(data.categories.labels.length);
    charts.primary.data = {
        labels: data.categories.labels,
        datasets: [{
            data: data.categories.values,
            backgroundColor: colors,
            borderColor: chartSettings.darkTheme ? '#333' : '#fff',
            borderWidth: 2,
            hoverOffset: 10
        }]
    };

    // Update category breakdown list
    updateCategoryBreakdownList(data.categories, colors);

    // Update trend chart
    charts.trend.data = {
        labels: data.trend.labels,
        datasets: [{
            label: 'Daily Spending',
            data: data.trend.values,
            borderColor: colors[0],
            backgroundColor: colors[0] + '20',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: colors[0],
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    };

    // Update monthly chart
    charts.monthly.data = {
        labels: data.monthly.labels,
        datasets: [{
            label: 'Monthly Expenses',
            data: data.monthly.values,
            backgroundColor: colors.slice(0, data.monthly.labels.length),
            borderColor: colors.slice(0, data.monthly.labels.length),
            borderWidth: 1,
            borderRadius: 5
        }]
    };

    // Update account chart
    charts.account.data = {
        labels: data.accounts.labels,
        datasets: [{
            data: data.accounts.values,
            backgroundColor: colors.slice(0, data.accounts.labels.length),
            borderColor: chartSettings.darkTheme ? '#333' : '#fff',
            borderWidth: 2
        }]
    };

    // Refresh all charts
    Object.values(charts).forEach(chart => chart.update());
}

function updateCategoryBreakdownList(categoriesData, colors) {
    const container = document.getElementById('category-breakdown-list');
    
    if (!categoriesData.labels || categoriesData.labels.length === 0) {
        container.innerHTML = `
            <div class="breakdown-header">No spending data available</div>
            <div class="text-center text-muted">
                <i data-feather="inbox" style="width: 48px; height: 48px;"></i>
                <p>Upload transactions to see category breakdown</p>
            </div>
        `;
        feather.replace();
        return;
    }

    const total = categoriesData.values.reduce((sum, value) => sum + value, 0);
    
    let html = `
        <div class="breakdown-header">Category Breakdown</div>
        <div class="breakdown-total">
            <h6>Total Expenses</h6>
            <h4>$${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h4>
        </div>
    `;

    categoriesData.labels.forEach((label, index) => {
        const value = categoriesData.values[index];
        const percentage = ((value / total) * 100).toFixed(1);
        const color = colors[index];

        html += `
            <div class="category-item">
                <div class="category-color" style="background-color: ${color};"></div>
                <div class="category-info">
                    <div class="category-name">${label}</div>
                    <div class="category-amount">$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    <div class="category-progress">
                        <div class="category-progress-bar" style="width: ${percentage}%; background-color: ${color};"></div>
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
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }, 200);
}

function updatePrimaryChart() {
    const chartType = document.getElementById('chart-type').value;
    charts.primary.config.type = chartType;
    charts.primary.update();
}

function toggleView(viewType) {
    if (viewType === 'category-breakdown') {
        const chart = document.querySelector('#primary-chart').closest('.col-lg-6');
        const breakdown = document.querySelector('#category-breakdown-list').closest('.col-lg-6');
        
        if (chart.style.display === 'none') {
            chart.style.display = 'block';
            breakdown.classList.remove('col-lg-12');
            breakdown.classList.add('col-lg-6');
        } else {
            chart.style.display = 'none';
            breakdown.classList.remove('col-lg-6');
            breakdown.classList.add('col-lg-12');
        }
    }
}

function updateSummaryCards(data) {
    document.getElementById('total-expenses').textContent = '$' + data.summary.total.toLocaleString();
    document.getElementById('avg-monthly').textContent = '$' + data.summary.avgMonthly.toLocaleString();
    document.getElementById('top-category').textContent = data.summary.topCategory || 'N/A';
    document.getElementById('top-category-amount').textContent = '$' + (data.summary.topCategoryAmount || 0).toLocaleString();
    document.getElementById('categories-count').textContent = data.summary.categoriesCount;
    
    const period = document.getElementById('time-period').value;
    const periodText = getPeriodText(period);
    document.getElementById('expense-period').textContent = periodText;
}

function updateFunStats(data) {
    const funStatsContainer = document.getElementById('fun-stats');
    const stats = calculateFunStats(data);
    
    funStatsContainer.innerHTML = '';
    
    stats.forEach(stat => {
        const statCard = document.createElement('div');
        statCard.className = 'col-md-3 mb-3';
        statCard.innerHTML = `
            <div class="fun-stat-card">
                <h6>${stat.title}</h6>
                <h4>${stat.value}</h4>
                <small>${stat.description}</small>
            </div>
        `;
        funStatsContainer.appendChild(statCard);
    });
}

function calculateFunStats(data) {
    const stats = [];
    
    if (data.summary.total > 0) {
        // Daily average
        const dailyAvg = data.summary.total / (data.trend.labels.length || 1);
        stats.push({
            title: '☕ Daily Coffee Money',
            value: '$' + dailyAvg.toFixed(2),
            description: 'Average daily spending'
        });
        
        // Percentage of income (assuming 5000 monthly income)
        const monthlyIncome = 5000;
        const percentage = ((data.summary.avgMonthly / monthlyIncome) * 100).toFixed(1);
        stats.push({
            title: '📊 Budget Impact',
            value: percentage + '%',
            description: 'Of estimated monthly income'
        });
        
        // Spending streak
        const streak = calculateSpendingStreak(data.trend.values);
        stats.push({
            title: '🔥 Spending Streak',
            value: streak + ' days',
            description: 'Consecutive days with expenses'
        });
        
        // Favorite shopping day
        const favoriteDay = getFavoriteShoppingDay(data.trend.labels, data.trend.values);
        stats.push({
            title: '🛍️ Favorite Shopping Day',
            value: favoriteDay,
            description: 'Your highest spending day'
        });
    }
    
    return stats;
}

function calculateSpendingStreak(values) {
    let streak = 0;
    let currentStreak = 0;
    
    for (let i = values.length - 1; i >= 0; i--) {
        if (values[i] > 0) {
            currentStreak++;
        } else {
            break;
        }
    }
    
    return currentStreak;
}

function getFavoriteShoppingDay(labels, values) {
    let maxValue = 0;
    let maxDay = 'Monday';
    
    for (let i = 0; i < values.length; i++) {
        if (values[i] > maxValue) {
            maxValue = values[i];
            const date = new Date(labels[i]);
            maxDay = date.toLocaleDateString('en-US', { weekday: 'long' });
        }
    }
    
    return maxDay;
}

function getPeriodText(period) {
    const periods = {
        'last_30': 'Last 30 days',
        'last_90': 'Last 3 months',
        'last_180': 'Last 6 months',
        'last_365': 'Last year',
        'all': 'All time',
        'custom': 'Custom period'
    };
    
    return periods[period] || 'Selected period';
}

function getColors(count) {
    const scheme = colorSchemes[chartSettings.colorScheme] || colorSchemes.default;
    const colors = [];
    
    for (let i = 0; i < count; i++) {
        colors.push(scheme[i % scheme.length]);
    }
    
    return colors;
}

function animateChart(chartId) {
    const chartMap = {
        'primary-chart': 'primary',
        'trend-chart': 'trend',
        'monthly-chart': 'monthly',
        'account-chart': 'account'
    };
    
    const chart = charts[chartMap[chartId]];
    if (chart) {
        chart.canvas.parentElement.classList.add('chart-pulse');
        chart.update('active');
        
        setTimeout(() => {
            chart.canvas.parentElement.classList.remove('chart-pulse');
        }, 600);
    }
}

function downloadChart(chartId) {
    const chartMap = {
        'primary-chart': 'primary',
        'trend-chart': 'trend',
        'monthly-chart': 'monthly',
        'account-chart': 'account'
    };
    
    const chart = charts[chartMap[chartId]];
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}-${Date.now()}.png`;
        link.href = url;
        link.click();
    }
}

function exportAllCharts() {
    // Download each chart individually since we don't have JSZip
    Object.keys(charts).forEach((key, index) => {
        setTimeout(() => {
            const chart = charts[key];
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `${key}-chart-${Date.now()}.png`;
            link.href = url;
            link.click();
        }, index * 500); // Stagger downloads to avoid browser blocking
    });
    
    showAlert('Downloading all charts individually...', 'info');
}

function applyCustomization() {
    // Update settings
    chartSettings.colorScheme = document.getElementById('color-scheme').value;
    chartSettings.animationStyle = document.getElementById('animation-style').value;
    chartSettings.showAnimations = document.getElementById('show-animations').checked;
    chartSettings.showValues = document.getElementById('show-values').checked;
    chartSettings.showPercentages = document.getElementById('show-percentages').checked;
    chartSettings.darkTheme = document.getElementById('dark-theme').checked;
    
    // Update chart options
    Object.values(charts).forEach(chart => {
        chart.options = getChartOptions(chart.config.type);
    });
    
    // Reload data with new settings
    loadChartData();
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('customizeModal'));
    modal.hide();
    
    showAlert('Chart customization applied!', 'success');
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
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}