from flask import Flask, request, redirect, url_for, render_template_string
import os
import sqlite3

app = Flask(__name__)

# データベースの保存場所
DATABASE_PATH = "data.db"

# データベース初期化
def init_db():
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY,
                content TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

# ホーム画面
@app.route('/')
def home():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_iphone13 = 'iphone' in user_agent and '13' in user_agent

    # UI調整: PCとiPhone13でレイアウトを変更
    if is_iphone13:
        ui_style = '''
            body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
            input { width: 90%; padding: 10px; margin-bottom: 10px; }
            button { width: 90%; padding: 10px; }
        '''
    else:
        ui_style = '''
            body { font-family: Arial, sans-serif; text-align: center; margin: 100px auto; width: 60%; }
            input { width: 80%; padding: 15px; margin-bottom: 15px; font-size: 1.2rem; }
            button { width: 40%; padding: 15px; font-size: 1.2rem; }
        '''

    # 言語選択
    language = request.args.get('lang', 'ja')
    if language == 'hi':
        title = "डेटा प्रबंधन"
        send_button = "भेजें"
        view_data_link = "डेटा देखें"
    else:
        title = "データ管理"
        send_button = "送信"
        view_data_link = "データを見る"

    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{language}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            {ui_style}
            select {{ margin: 10px; padding: 5px; }}
        </style>
    </head>
    <body>
        <form method="GET" style="text-align: right;">
            <label for="lang">言語選択:</label>
            <select name="lang" id="lang" onchange="this.form.submit()">
                <option value="ja" {"selected" if language == "ja" else ""}>日本語</option>
                <option value="hi" {"selected" if language == "hi" else ""}>हिन्दी</option>
            </select>
        </form>
        <h1>{title}</h1>
        <form action="/submit-data" method="POST">
            <input type="text" name="content" placeholder="データを入力" required>
            <br>
            <button type="submit">{send_button}</button>
        </form>
        <br>
        <a href="/view-data?lang={language}">{view_data_link}</a>
    </body>
    </html>
    ''')

# データの送信
@app.route('/submit-data', methods=['POST'])
def submit_data():
    content = request.form.get('content')
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO data (content, created_at) VALUES (?, datetime("now"))', (content,))
    conn.commit()
    conn.close()
    return redirect('/')

# データ閲覧
@app.route('/view-data')
def view_data():
    language = request.args.get('lang', 'ja')
    if language == 'hi':
        title = "डेटा देखें"
    else:
        title = "データを見る"

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, created_at FROM data')
    rows = cursor.fetchall()
    conn.close()

    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{language}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin: 100px auto; width: 60%; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <ul>
            {''.join(f'<li>{row[1]} ({row[2]})</li>' for row in rows)}
        </ul>
        <a href="/">戻る</a>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
