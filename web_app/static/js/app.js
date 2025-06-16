document.getElementById('upload-form').addEventListener('submit', async function(e){
    e.preventDefault();
    const formData = new FormData(this);
    const response = await fetch('/predict', {method: 'POST', body: formData});
    const data = await response.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    renderTable(data);
    renderChart(data);
    document.getElementById('download-links').style.display = 'block';
});

document.getElementById('model-upload-form').addEventListener('submit', async function(e){
    e.preventDefault();
    const formData = new FormData(this);
    const response = await fetch('/upload_model', {method: 'POST', body: formData});
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
});

function renderTable(data) {
    const container = document.getElementById('table-container');
    const table = document.createElement('table');
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
