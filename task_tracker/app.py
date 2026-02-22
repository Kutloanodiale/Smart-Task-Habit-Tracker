import mysql.connector
from flask import Flask,render_template,make_response, request,jsonify,redirect,session,flash
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)#web app
app.secret_key = "123" 

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="tracker_user",
        password="StrongPassword123",
        database="smart_tracker"
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
    
    password_ha = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, password_ha)
    )
    db.commit()
    cursor.close()
    db.close()
    return True




@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user:
            flash("Username not found!", "error")
            return redirect("/")  # redirect clears form

        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password!", "error")
            return redirect("/")  # redirect clears form

        # Successful login
        session["username"] = username
        flash("Logged in successfully!", "success")
        return redirect("/home")

    # GET request → show login form with headers to prevent caching
    resp = make_response(render_template("login.html"))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp # fresh empty form



@app.route("/c_password", methods=["GET", "POST"])
def register():
    #grabs the values the user typed into your form fields
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        # Check passwords match
        if password != confirm:
            flash("Passwords do not match!")
            return redirect("/c_password")

        # Call your function
        if register_user(username, email, password):
            flash("Account created successfully!")
            return redirect("/")
        else:
            flash("Username or email already exists!")
            return redirect("/c_password")

    return render_template("create_password.html")



@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND email=%s",
            (username, email)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            # Correct username and email → go to new password page
            return redirect(f"/reset_password/{username}")
        else:
            flash("Username or email not found!")
            return render_template("forgot_pass.html")

    return render_template("forgot_pass.html")


@app.route("/reset_password/<username>", methods=["GET", "POST"])
def reset_password(username):
    if request.method == "POST":
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Passwords do not match!")
            return render_template("reset_password.html", username=username)

        # Hash the new password and update the database
        password_hash = generate_password_hash(password)
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE username=%s",
            (password_hash, username)
        )
        db.commit()
        cursor.close()
        db.close()

        flash("Password updated successfully!")
        return redirect("/")

    return render_template("reset_password.html", username=username)



@app.route("/add",methods=["GET","POST"])#when pressing button add task you go to a   different web page
def add_task():
    
    if request.method == "POST":
        task_name = request.form["title"]
        prio = request.form["priority"]
        due_dt = request.form["due_date"]

        priority_map = {"Low": 1, "Medium": 2, "High": 3}
        prio = priority_map.get(prio, 1)  # default = 1 (Low)

        db = get_db_connection()
        cursor  =db.cursor()

        cursor.execute(
            "INSERT INTO tasks (title,priority,due_date) VALUES (%s, %s, %s)",
            (task_name,prio,due_dt)
        )
        db.commit()
        cursor.close()
        db.close()
        flash(f"Task '{task_name}' added successfully!")
        return redirect("/home")  # stay on the add task page

    return render_template("add_task.html")

def load_suggested_tasks():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT title, priority, due_date FROM tasks WHERE priority=%s ORDER BY due_date ASC LIMIT 2",
        ("high",)
    )
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return tasks


def load_tasks():
    db =  get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT title, priority, due_date FROM tasks ORDER BY due_date ASC")
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return tasks
    return []



@app.route("/home")
def home():
    if "username" not in session:
        flash("You must log in first!", "login")
        return redirect("/")

    tasks = load_tasks()               # all tasks
    suggested = load_suggested_tasks() # top 2 high-priority tasks

    return render_template(
        "index.html",
        username=session["username"],
        tasks=tasks,
        suggested=suggested
    )



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
