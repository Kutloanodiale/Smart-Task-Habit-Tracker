import mysql.connector
from flask import Flask, render_template, request,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)#web app
app.secret_key = "your_secret_key_here" 

def get_db_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "Kutlw!"
    )
    

def register_user(username, email, password):
    db = get_db_connection()#connection to the database
    cursor = db.cursor()

    # does user exist?
    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    if cursor.fetchone():
        cursor.close()
        db.close()
        return False 
    else:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        db.commit()
        cursor.close()
        db.close()
        return True


def login_user(username, password):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user["password_hash"], password):
        return user
    return None

def add_task(task_name,prio,due_dt):
    db = get_db_connection()
    cursor  =db.cursor()

    cursor.execute(
        "INSERT INTO tasks (title,priority,due_date) VALUES (?,?,?)",
        (task_name,prio,due_dt)
    )
    db.commit()
    cursor.close()
    db.close()
    print("Saving:", task_name)

def suggest_task():
    #suggest apps that have been the for a long time and have a high priority
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
    "SELECT * FROM tasks WHERE priority = ? ORDER BY timestamp ASC LIMIT 2",
    (high,)
)

    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results


def load_tasks():
    db =  get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT title, priority, due_date FROM tasks ORDER BY priority ASC, timestamp ASC")
    tasks = cursor.fetchall()
    db.close()
    return tasks
    return []



@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home")
def home():
    tasks = load_tasks()
    return render_template("index.html",tasks=tasks) # when opening the website "/" show index.html

@app.route("/add")#when pressing button add task you go to a   different web page
def add_task():
    return render_template("add_task.html")#show the html show the add_task.html page 

if __name__ == "__main__":
    app.run(debug=True)