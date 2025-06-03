from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
# app.secret_key = 'secret'  # Weak session secret

# Setup database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, comment TEXT, created_at DATE);
    """)
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    stored_comments = get_comments()
    if request.method == 'POST':
        comment = request.form['comment']
        return render_template('xss_dashboard.html', comment=f"<p><b>Your Comment:</b> {comment}</p>", stored_comments=stored_comments)
    return render_template('xss_dashboard.html', stored_comments=stored_comments)

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.method == 'POST':
        userInput = request.form['userInput']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (comment, created_at) VALUES (?, CURRENT_TIMESTAMP)", (userInput,))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/reset', methods=['GET', 'POST'])
def reset_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.executescript("DELETE FROM comments")
    conn.close()
    return redirect('/')

def get_comments():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=8089, debug=True)