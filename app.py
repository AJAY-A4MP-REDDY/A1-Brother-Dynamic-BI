import pandas as pd
import json
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>A1 Brother Dynamic BI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #eef2f3; margin: 0; padding: 20px; }
        .header { background: #1a237e; color: white; padding: 15px; text-align: center; border-radius: 15px; margin-bottom: 20px; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .chart-container { background: white; padding: 15px; border-radius: 15px; border: 1px solid #ddd; }
        select { padding: 8px; border-radius: 5px; margin: 5px; width: 40%; }
        .btn { background: #1a237e; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>📊 A1 Brother Dynamic Power BI</h1></div>
    
    <div class="card" style="text-align:center;">
        <h3>1. Select Any File</h3>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit" class="btn">Load Data</button>
        </form>
    </div>

    {% if f_type == 'csv' %}
    <div class="card">
        <h3>2. Dashboard Designer (Manual Selection)</h3>
        <p>Select columns for each chart type:</p>
        <div class="grid" id="dashboard"></div>
    </div>

    <script>
        var rawData = {{ df_json | safe }};
        var columns = {{ cols | safe }};
        var chartTypes = ['bar', 'line', 'scatter', 'pie', 'area', 'donut', 'funnel', 'violin', 'box', 'histogram'];

        var dashboard = document.getElementById('dashboard');

        chartTypes.forEach((type, i) => {
            var container = document.createElement('div');
            container.className = 'chart-container';
            container.innerHTML = `
                <h4 style="text-transform: capitalize;">${type} Chart Settings</h4>
                <select id="x_${i}">${columns.map(c => `<option>${c}</option>`).join('')}</select>
                <select id="y_${i}">${columns.map(c => `<option>${c}</option>`).join('')}</select>
                <button class="btn" onclick="updateChart(${i}, '${type}')">Update Chart</button>
                <div id="plot_${i}"></div>
            `;
            dashboard.appendChild(container);
            updateChart(i, type);
        });

        function updateChart(index, type) {
            var xCol = document.getElementById('x_' + index).value;
            var yCol = document.getElementById('y_' + index).value;

            var xData = rawData.map(row => row[xCol]);
            var yData = rawData.map(row => row[yCol]);

            var trace = { x: xData.slice(0,10), y: yData.slice(0,10), type: type };
            if(type === 'pie' || type === 'donut') {
                trace = { labels: xData.slice(0,5), values: yData.slice(0,5), type: 'pie' };
                if(type === 'donut') trace.hole = 0.4;
            }
            if(type === 'line') { trace.type = 'scatter'; trace.mode = 'lines+markers'; }
            if(type === 'scatter') { trace.type = 'scatter'; trace.mode = 'markers'; }
            if(type === 'area') { trace.type = 'scatter'; trace.fill = 'tozeroy'; }

            var layout = { title: type.toUpperCase() + ': ' + yCol, height: 350 };
            Plotly.newPlot('plot_' + index, [trace], layout);
        }
    </script>

    {% elif f_type == 'image' %}
        <div class="card" style="text-align:center;"><img src="{{ img_data }}" style="max-width:100%;"></div>
    {% elif f_type == 'other' %}
        <div class="card"><h3>✅ File Accepted: {{ f_name }}</h3></div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return render_template_string(HTML_TEMPLATE)
        fname = file.filename.lower()
        if fname.endswith('.csv'):
            df = pd.read_csv(file)
            return render_template_string(HTML_TEMPLATE, f_type='csv',
                                          df_json=df.to_json(orient='records'),
                                          cols=df.columns.tolist())
        elif fname.endswith(('.png', '.jpg', '.jpeg')):
            import base64
            img_data = f"data:image/png;base64,{base64.b64encode(file.read()).decode()}"
            return render_template_string(HTML_TEMPLATE, f_type='image', img_data=img_data)
        else:
            return render_template_string(HTML_TEMPLATE, f_type='other', f_name=file.filename)
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
