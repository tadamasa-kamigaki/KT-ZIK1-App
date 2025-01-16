from flask import Flask, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# データベースの保存場所
DATABASE_PATH = "/var/www/KT-ZIK1/data.db"

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

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>KT-ZIK1 Test Page</title>
    </head>
    <body>
        <h1>Welcome to KT-ZIK1 Web Application!</h1>
        <a href="/send-form">Send Data</a><br>
        <a href="/view-data">View Data</a>
    </body>
    </html>
    '''

@app.route('/send-form', methods=['GET', 'POST'])
def send_form():
    if request.method == 'POST':
        content = request.form.get('content', '')
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO data (content, created_at) VALUES (?, datetime("now"))', (content,))
        conn.commit()
        conn.close()
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Send Data</title>
    </head>
    <body>
        <form method="POST">
            <label for="content">Content:</label>
            <input type="text" id="content" name="content">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    '''

@app.route('/view-data')
def view_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, created_at FROM data')
    rows = cursor.fetchall()
    conn.close()
    return '<br>'.join(f'{row[0]}: {row[1]} ({row[2]})' for row in rows)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
