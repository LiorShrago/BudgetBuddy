// Chart utilities and configurations
const ChartConfig = {
    // Default colors for categories
    colors: [
        '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
        '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
    ],
    
    // Common chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#ffffff',
                    usePointStyle: true
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#ffffff'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            y: {
                ticks: {
                    color: '#ffffff',
                    callback: function(value) {
                        return '$' + value.toFixed(2);
                    }
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        }
    }
};

// Create spending trend chart
function createSpendingTrendChart(ctx, data) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Spending',
                data: data.spending,
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Income',
                data: data.income,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...ChartConfig.defaultOptions,
            plugins: {
                ...ChartConfig.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Spending vs Income Trend',
                    color: '#ffffff'
                }
            }
        }
    });
}

// Create budget progress chart
function createBudgetProgressChart(ctx, data) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.categories,
            datasets: [{
                label: 'Budgeted',
                data: data.budgeted,
                backgroundColor: 'rgba(23, 162, 184, 0.6)',
                borderColor: '#17a2b8',
                borderWidth: 1
            }, {
                label: 'Spent',
                data: data.spent,
                backgroundColor: 'rgba(220, 53, 69, 0.6)',
                borderColor: '#dc3545',
                borderWidth: 1
            }]
        },
        options: {
            ...ChartConfig.defaultOptions,
            plugins: {
                ...ChartConfig.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Budget vs Actual Spending',
                    color: '#ffffff'
                }
            }
        }
    });
}

// Create monthly spending chart
function createMonthlySpendingChart(ctx, data) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.months,
            datasets: [{
                label: 'Monthly Spending',
                data: data.amounts,
                backgroundColor: ChartConfig.colors.map(color => color + '80'),
                borderColor: ChartConfig.colors,
                borderWidth: 1
            }]
        },
        options: {
            ...ChartConfig.defaultOptions,
            plugins: {
                ...ChartConfig.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Monthly Spending Overview',
                    color: '#ffffff'
                }
            }
        }
    });
}

// Utility function to generate chart colors
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(ChartConfig.colors[i % ChartConfig.colors.length]);
    }
    return colors;
}

// Export functions for use in other scripts
window.ChartUtils = {
    createSpendingTrendChart,
    createBudgetProgressChart,
    createMonthlySpendingChart,
    generateColors,
    config: ChartConfig
};
