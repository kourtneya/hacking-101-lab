from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'  # Weak session secret

# Setup database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, is_admin INTEGER);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('admin', 'admin', 1);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('user', 'pass', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('anakin', 'skywalker123', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('ashoka', 'tano456', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('leia', 'ortega789', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('obiwan', 'kenobi135', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('vader', 'darth246', 0);
    INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('yoda', 'master357', 0);
    """)
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vulnerable to SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['is_admin'] = user[3]
            return redirect('/dashboard')
        else:
            return render_template('login.html', response="Login Failed")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        # XSS vulnerability
        comment = request.form['comment']
        return render_template('dashboard.html', username=session['username'], comment=f"Your Comment: {comment} ")
    return render_template('dashboard.html', username=session['username'])

@app.route('/admin')
def admin():
    # Broken Access Control
    if not session.get('is_admin'):
        return render_template('admin.html', access_status="Access Denied")
    return render_template('admin.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    # CSRF Vulnerability
    new_pass = request.form['new_password']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.executescript(f"UPDATE users SET password = '{new_pass}' WHERE username = '{session['username']}'")
    conn.commit()
    conn.close()
    return render_template('response.html', response="Password Changed!")

@app.route('/users', methods=['POST'])
def find_users():
    username = request.form['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users where username='{username}'")
    users = cursor.fetchall()
    conn.close()

    if not users:
        return render_template('users.html')

    return render_template('users.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=8088, debug=True)