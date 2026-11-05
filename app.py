from flask import Flask, render_template_string, request, redirect, url_for, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOTÉC 夜序 - 陪玩營運管理後台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f8f9fa; font-family: sans-serif; }
        .sidebar { min-height: 100vh; background: #212529; color: #fff; }
        .sidebar a { color: #adb5bd; text-decoration: none; padding: 10px 20px; display: block; border-radius: 5px; margin-bottom: 5px; }
        .sidebar a:hover, .sidebar a.active { background: #0d6efd; color: #fff; }
        .card { border: none; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); margin-bottom: 20px; border-radius: 10px; }
        .table-custom th { background-color: #343a40; color: white; }
    </style>
</head>
<body>
<div class="container-fluid">
    <div class="row">
        <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse p-3">
            <h4 class="text-white text-center py-3">NOTÉC 夜序</h4>
            <hr class="text-secondary">
            <ul class="nav flex-column">
                <li class="nav-item"><a href="#" class="active"><i class="fas fa-chart-line me-2"></i> 營運與分帳設定</a></li>
                <li class="nav-item"><a href="/export_excel" class="text-success"><i class="fas fa-file-excel me-2"></i> 一鍵匯出 Excel</a></li>
            </ul>
        </nav>
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
            <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                <h1 class="h2">📊 團隊分帳與機器人參數後台</h1>
                <span class="badge bg-success fs-6">系統連線正常</span>
            </div>
            <div class="card p-4">
                <h4 class="mb-3"><i class="fas fa-percentage text-primary me-2"></i> 人員分帳比例設定</h4>
                <form action="/update_ratios" method="POST">
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover align-middle">
                            <thead class="table-custom">
                                <tr>
                                    <th>代號</th>
                                    <th>人員名稱</th>
                                    <th>無人局 / 代肝 比例 (%)</th>
                                    <th>A大模式 比例 (%)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in configs %}
                                <tr>
                                    <td><strong>{{ row.role_code }}</strong></td>
                                    <td>{{ row.member_name }}</td>
                                    <td>
                                        <div class="input-group">
                                            <input type="number" name="normal_{{ row.role_code }}" value="{{ (row.normal_ratio * 100) | int }}" class="form-control" required>
                                            <span class="input-group-text">%</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group">
                                            <input type="number" name="special_{{ row.role_code }}" value="{{ (row.special_ratio * 100) | int }}" class="form-control" required>
                                            <span class="input-group-text">%</span>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    <button type="submit" class="btn btn-primary px-4 mt-2">儲存並即時更新設定</button>
                </form>
            </div>
        </main>
    </div>
</div>
</body>
</html>
'''

@app.route('/')
def index():
    conn = get_db_connection()
    configs = conn.execute('SELECT * FROM split_configs').fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, configs=configs)

@app.route('/update_ratios', methods=['POST'])
def update_ratios():
    conn = get_db_connection()
    cursor = conn.cursor()
    for code in ['A', 'B', 'C']:
        normal_val = float(request.form.get(f'normal_{code}', 0)) / 100.0
        special_val = float(request.form.get(f'special_{code}', 0)) / 100.0
        cursor.execute('UPDATE split_configs SET normal_ratio = ?, special_ratio = ? WHERE role_code = ?', (normal_val, special_val, code))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/export_excel')
def export_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_consume = pd.DataFrame({'顧客': ['7N', '-', '-'], '消費金額': [300, 0, 0]})
        df_consume.to_excel(writer, sheet_name='消費金額', index=False)
        df_settings = pd.DataFrame({
            '代號': ['A', 'B', 'C', '合計'],
            '人員名稱': ['En', '小樂', '股東', ''],
            '無人局/代肝比例': ['60%', '30%', '10%', '100%'],
            'A大模式比例': ['70%', '30%', '0%', '100%']
        })
        df_settings.to_excel(writer, sheet_name='補給總額', index=False)
        for project in ['無人局', '代肝1億', 'A大專案']:
            df_project = pd.DataFrame(columns=['時間', '顧客', '接單人', '單價/總收入', '成本/平台扣費', '淨利潤 (x)', 'A (En) 分帳', 'B (小樂) 分帳', 'C (股東) 分帳'])
            df_project.to_excel(writer, sheet_name=project, index=False)
    output.seek(0)
    return send_file(output, download_name="NOTEC_NightOrder_Report.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    import os
    if not os.path.exists('database.db'):
        import database
        database.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
