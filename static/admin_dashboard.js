        document.addEventListener('DOMContentLoaded', () => {
            const btn = document.getElementById('confirmLogoutBtn');
            btn.addEventListener('click', () => {
                document.getElementById('logoutForm').submit();
            });
        });

        Chart.register(ChartDataLabels); // register plugin

    let stockChart;

    async function pieStocks() {
    try {
        const res = await fetch('/admin_dashboard/pieStock');
        const data = await res.json();

        const ctx = document.getElementById('stockChart').getContext('2d');
        if (stockChart) stockChart.destroy();

        const values = [data.out_of_stock ?? 0, data.on_stock ?? 0];

        stockChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Out of Stock', 'Available'],
            datasets: [{
            data: values,
            backgroundColor: ['#740000ff', '#0c47faff'],
            borderColor: '#ffffff',
            borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: {
                position: 'right',
                labels: {
                color: '#000',
                font: { size: 13 }
                }
            },
            tooltip: {
                callbacks: {
                label: (ctx) => `${ctx.label}: ${ctx.parsed}` // only number, no %
                }
            },
            // 🔹 Show integers inside the slices
            datalabels: {
                color: '#fff',
                font: {
                weight: 'bold',
                size: 14
                },
                formatter: (value) => {
                if (value === 0) return ''; // hide zero values
                return Math.round(value); // display only integer
                }
            }
            }
        },
        plugins: [ChartDataLabels]
        });
    } catch (err) {
        console.error("Error loading chart:", err);
    }
    }

    async function highStock(){
        const api = await fetch('/admin_dashboard/highStock');
        const data = await api.json();

        const highStock = document.getElementById('highStock');
        highStock.innerText = data.highstock;
    }
    async function lowStock(){
        const api = await fetch('/admin_dashboard/lowStock');
        const data = await api.json();

        const highStock = document.getElementById('lowStock');
        highStock.innerText = data.lowstock;

    }
    async function totalBenta(){
        const api = await fetch('/admin_dashboard/totalBenta');
        const data = await api.json();

        const totalBenta = document.getElementById('totalBenta');
        totalBenta.innerText = `₱ ${data.total}.00`;

    }

async function loadTopItems() {
  try {
    const res = await fetch('/admin_dashboard/topItems');
    const data = await res.json();

    const list = document.getElementById('topItemsList');
    list.innerHTML = data.map((item, i) => `
      <li class="mb-1 d-flex justify-content-between">
        <span>${i + 1}. ${item.name}</span>
        <span class="text-dark">${item.total_qty}</span>
      </li>
    `).join('');
  } catch (err) {
    console.error('Error loading top items:', err);
  }
}
    document.addEventListener('DOMContentLoaded', totalBenta);
    document.addEventListener('DOMContentLoaded', loadTopItems);
    document.addEventListener('DOMContentLoaded', lowStock);
    document.addEventListener('DOMContentLoaded', highStock);
    document.addEventListener("DOMContentLoaded", pieStocks);