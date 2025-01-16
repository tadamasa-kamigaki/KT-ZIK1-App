from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import os
import sqlite3
import traceback

app = Flask(__name__)

# データベースの保存場所
DATABASE_PATH = "inventory.db"

# データベース初期化
def init_db():
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                operation TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                item_name TEXT PRIMARY KEY,
                total_quantity INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>在庫管理アプリ</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
            input, button { margin: 10px; padding: 10px; width: 80%; }
            button { background-color: #007BFF; color: white; border: none; border-radius: 5px; }
            button:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h1>在庫管理アプリ</h1>
        <form action="/submit-data" method="POST">
            <input type="text" name="item_name" placeholder="品目名を入力" required>
            <input type="number" name="quantity" placeholder="数量を入力" required>
            <button type="submit" name="operation" value="入庫">入庫</button>
            <button type="submit" name="operation" value="出庫">出庫</button>
        </form>
        <br>
        <a href="/view-data">データを見る</a>
    </body>
    </html>
    ''')

@app.route('/submit-data', methods=['POST'])
def submit_data():
    item_name = request.form.get('item_name')
    quantity = int(request.form.get('quantity'))
    operation = request.form.get('operation')

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        if operation == '入庫':
            cursor.execute('''
                INSERT INTO inventory (item_name, quantity, operation) 
                VALUES (?, ?, ?)
            ''', (item_name, quantity, operation))
            cursor.execute('''
                INSERT INTO stock (item_name, total_quantity)
                VALUES (?, ?)
                ON CONFLICT(item_name) DO UPDATE SET total_quantity = total_quantity + ?
            ''', (item_name, quantity, quantity))
        elif operation == '出庫':
            cursor.execute('''
                INSERT INTO inventory (item_name, quantity, operation) 
                VALUES (?, ?, ?)
            ''', (item_name, -quantity, operation))
            cursor.execute('''
                INSERT INTO stock (item_name, total_quantity)
                VALUES (?, ?)
                ON CONFLICT(item_name) DO UPDATE SET total_quantity = total_quantity - ?
            ''', (item_name, -quantity, quantity))

        conn.commit()
    except Exception as e:
        print("データ送信エラー:", traceback.format_exc())
        return f"エラー: {e}", 500
    finally:
        conn.close()

    return redirect('/')

@app.route('/view-data')
def view_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT item_name, quantity, operation, created_at FROM inventory')
        inventory_data = cursor.fetchall()

        cursor.execute('SELECT item_name, total_quantity FROM stock')
        stock_data = cursor.fetchall()
    except Exception as e:
        print("データビューエラー:", traceback.format_exc())
        return f"エラー: {e}", 500
    finally:
        conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>データを見る</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 50px auto; width: 80%; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>履歴データ</h1>
        <table>
            <tr>
                <th>品目名</th>
                <th>数量</th>
                <th>操作</th>
                <th>日時</th>
            </tr>
            {% for row in inventory_data %}
            <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td></tr>
            {% endfor %}
        </table>
        <h1>現在の在庫</h1>
        <table>
            <tr>
                <th>品目名</th>
                <th>合計数量</th>
            </tr>
            {% for row in stock_data %}
            <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td></tr>
            {% endfor %}
        </table>
        <a href="/">戻る</a>
    </body>
    </html>
    ''', inventory_data=inventory_data, stock_data=stock_data)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
