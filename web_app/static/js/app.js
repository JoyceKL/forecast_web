document.getElementById('upload-form').addEventListener('submit', async function(e){
    e.preventDefault();
    document.getElementById('loading').style.display = 'block';
    const formData = new FormData(this);
    const response = await fetch('/predict', {method: 'POST', body: formData});
    const data = await response.json();
    document.getElementById('loading').style.display = 'none';
    if (data.error) {
        alert(data.error);
        return;
    }
    renderTable(data);
    renderChart(data);
    document.getElementById('download-links').style.display = 'block';
    updateStats(data);
});

document.getElementById('model-upload-form').addEventListener('submit', async function(e){
    e.preventDefault();
    const formData = new FormData(this);
    const response = await fetch('/upload_model/submit', {method: 'POST', body: formData});
    const data = await response.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    const select = document.getElementById('model-select');
    const opt = document.createElement('option');
    opt.value = data.name;
    opt.textContent = data.name;
    select.appendChild(opt);
    this.reset();
    alert('Model uploaded');
    fetchStats();
});

async function fetchStats() {
    const resp = await fetch('/stats');
    const data = await resp.json();
    updateStats(data);
}

function updateStats(data) {
    if (data.model_count !== undefined) {
        document.getElementById('model-count').textContent = data.model_count;
    }
    if (data.run_count !== undefined) {
        document.getElementById('run-count').textContent = data.run_count;
    }
    if (data.last_run !== undefined) {
        document.getElementById('last-run').textContent = data.last_run || 'N/A';
    }
}

document.addEventListener('DOMContentLoaded', fetchStats);

function renderTable(data) {
    const container = document.getElementById('table-container');
    const table = document.createElement('table');
    table.className = 'table table-dark table-bordered';
    let html = '<tr><th>Date</th>';
    if (data.actual) {
        html += '<th>Actual</th>';
    }
    html += '<th>Predicted</th></tr>';
    for (let i = 0; i < data.dates.length; i++) {
        html += '<tr><td>' + data.dates[i] + '</td>';
        if (data.actual) {
            html += '<td>' + (data.actual[i] ?? '') + '</td>';
        }
        html += '<td>' + data.predicted[i] + '</td></tr>';
    }
    table.innerHTML = html;
    container.innerHTML = '';
    container.appendChild(table);
}

function renderChart(data) {
    const ctx = document.getElementById('chart').getContext('2d');
    if (window.resultChart) {
        window.resultChart.destroy();
    }
    window.resultChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [
                data.actual ? {
                    label: 'Actual',
                    data: data.actual,
                    borderColor: 'blue',
                    fill: false
                } : null,
                {
                    label: 'Predicted',
                    data: data.predicted,
                    borderColor: 'red',
                    fill: false
                }
            ].filter(Boolean)
        },
        options: {
            responsive: true,
            scales: {
                x: {display: true},
                y: {display: true}
            }
        }
    });
}
