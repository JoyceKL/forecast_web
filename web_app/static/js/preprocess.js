document.getElementById('preprocess-form').addEventListener('submit', async function(e){
    e.preventDefault();
    const formData = new FormData(this);
    const resp = await fetch('/run_preprocess', {method: 'POST', body: formData});
    const data = await resp.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    renderPreview('train-table', data.train_preview);
    renderPreview('test-table', data.test_preview);
    document.getElementById('stats').textContent = JSON.stringify(data.stats, null, 2);
    document.getElementById('result').style.display = 'block';
});

function renderPreview(id, rows) {
    const container = document.getElementById(id);
    const table = document.createElement('table');
    table.className = 'table table-dark table-bordered table-sm';
    if (!rows.length) { container.innerHTML = 'No data'; return; }
    let headers = Object.keys(rows[0]);
    let html = '<tr>' + headers.map(h=>'<th>'+h+'</th>').join('') + '</tr>';
    for (const row of rows) {
        html += '<tr>' + headers.map(h=>'<td>'+row[h]+'</td>').join('') + '</tr>';
    }
    table.innerHTML = html;
    container.innerHTML = '';
    container.appendChild(table);
}
