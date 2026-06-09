/* dashboard.js – Chart.js integration for FinanceGestor */

document.addEventListener('DOMContentLoaded', () => {
    loadPieChart();
    loadBarChart();
});

/* ── Color Palette ── */
const COLORS = {
    primary:  '#6366f1',
    success:  '#10b981',
    danger:   '#ef4444',
    warning:  '#f59e0b',
    info:     '#3b82f6',
    purple:   '#8b5cf6',
    pink:     '#ec4899',
    teal:     '#14b8a6',
    orange:   '#f97316',
};

const PALETTE = Object.values(COLORS);

/* ── Shared Chart defaults ── */
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size   = 12;
Chart.defaults.color       = '#64748b';

/* =========================================================
   PIE CHART – Despesas por Categoria
   ========================================================= */
async function loadPieChart() {
    const ctx = document.getElementById('expensesPieChart');
    if (!ctx) return;

    try {
        const res  = await fetch('/api/chart/expenses-by-category');
        const data = await res.json();

        if (!data.labels.length) {
            ctx.classList.add('d-none');
            document.getElementById('pieChartEmpty')?.classList.remove('d-none');
            return;
        }

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data:            data.data,
                    backgroundColor: PALETTE.slice(0, data.data.length),
                    borderWidth:     2,
                    borderColor:     '#fff',
                    hoverOffset:     8,
                }]
            },
            options: {
                responsive:          true,
                maintainAspectRatio: true,
                cutout:              '62%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding:     14,
                            usePointStyle: true,
                            pointStyle:  'circle',
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct   = ((ctx.parsed / total) * 100).toFixed(1);
                                return ` Kz ${formatCurrency(ctx.parsed)} (${pct}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate:  true,
                    animateScale:   true,
                    duration:       700,
                    easing:         'easeOutQuart'
                }
            }
        });
    } catch (err) {
        console.error('Pie chart error:', err);
    }
}

/* =========================================================
   BAR CHART – Receitas vs Despesas por Mês
   ========================================================= */
async function loadBarChart() {
    const ctx = document.getElementById('monthlyBarChart');
    if (!ctx) return;

    try {
        const res  = await fetch('/api/chart/monthly-summary');
        const data = await res.json();

        const yearBadge = document.getElementById('chartYear');
        if (yearBadge) yearBadge.textContent = data.year;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label:           'Receitas',
                        data:            data.income,
                        backgroundColor: 'rgba(16, 185, 129, 0.75)',
                        borderColor:     '#10b981',
                        borderWidth:     1.5,
                        borderRadius:    6,
                        borderSkipped:   false,
                    },
                    {
                        label:           'Despesas',
                        data:            data.expense,
                        backgroundColor: 'rgba(239, 68, 68, 0.75)',
                        borderColor:     '#ef4444',
                        borderWidth:     1.5,
                        borderRadius:    6,
                        borderSkipped:   false,
                    }
                ]
            },
            options: {
                responsive:          true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 16,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.dataset.label}: Kz ${formatCurrency(ctx.parsed.y)}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: { size: 11 },
                            callback: v => 'Kz ' + formatCurrency(v)
                        }
                    }
                },
                animation: {
                    duration: 700,
                    easing:   'easeOutQuart'
                }
            }
        });
    } catch (err) {
        console.error('Bar chart error:', err);
    }
}

/* ── Utility Functions ── */

/**
 * Format currency value as Angolan Kwanza
 * 1500 -> 1.500,00 (European style)
 */
function formatCurrency(value) {
    if (!value && value !== 0) return '0,00';
    
    const num = Number(value);
    return num.toLocaleString('pt-AO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
        useGrouping: true
    });
}

/**
 * Format as Kwanza with symbol
 * 1500 -> Kz 1.500,00
 */
function formatKwanza(value) {
    return 'Kz ' + formatCurrency(value);
}
