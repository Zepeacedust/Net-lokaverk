from flask import Flask, render_template as rend, session, request, redirect, url_for
import hashlib
import binascii
import os
import pymysql
import secrets
app = Flask(__name__)
# todo connecta rétt
connection = pymysql.connect(host='tsuts.tskoli.is', port=3306, user='0903032790',
                             password='mypassword', database='0903032790_users', autocommit=True)
cursor = connection.cursor()
# alltaf gaman að fara overboard
app.secret_key = secrets.token_hex(255)

# stal smá kóða af fólki sem veit betur


def hash_password(password):
    # Hash a password for storing.
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac(
        'sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    # Verify a stored password against one provided by user
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode(
        'utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


@app.route('/')
def index():
    cursor.execute("select * from posts;")
    posts = cursor.fetchall()
    print(session)
    if "user" not in session.keys():
        session["user"] = {"name": None, "pass": None}
    user = session["user"]
    return rend("index.html", user=user, posts=posts)


@app.route("/signup")
def signup():
    return rend("signup.html", code=None)


@app.route("/signup/create", methods=['POST'])
def addusr():
    r = request.form
    print(r)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    if request.form['username'] in map(lambda x: x[0], rows):
        return rend("signup.html", code=1)
    cursor.execute("INSERT INTO users (username, pass) VALUES (%s, %s);" %
                   (connection.escape(r['username']),
                    connection.escape(hash_password(r['password']))))
    session["user"] = {"name": r["username"],
                       "pass": hash_password(r['password'])}
    return redirect(url_for("index"))


@app.route("/login")
def login_page():
    return rend("login.html", code=None)


@app.route("/update/<post>")
def update_screen(post):
    print(session)
    if session["user"]["name"] != None:
        cursor.execute("select * from posts where id=%s;" % (post))
        post = cursor.fetchall()[0]
        return rend("update.html", post=post)
    else:
        return redirect(url_for("index"))


@app.route("/update/<post>/change", methods=["POST"])
def update(post):
    change = request.form["change"]
    cursor.execute("UPDATE posts SET body = %s WHERE ID = %s;" %
                   (connection.escape(change), connection.escape(post)))
    return redirect(url_for("index"))


@app.route("/delete/<post>")
def delete(post):
    cursor.execute("select * from posts where id=%s;" % (post))
    check = cursor.fetchall()[0]
    if session["user"]["name"] == check[3]:
        cursor.execute("delete from posts where id=%s;" % (post))
    return redirect(url_for("index"))


@app.route("/post", methods=['POST'])
def post():
    r = request.form
    print(r)
    cursor.execute("insert into posts(Id, title, body, author) values(0, %s, %s, %s)"
                   %
                   (
                       connection.escape(r['title']),
                       connection.escape(r['body']),
                       connection.escape(r['name'])))
    return redirect(url_for("index"))


@app.route("/login/process", methods=['POST'])
def login():
    r = request.form
    cursor.execute("""select * from users where username=%s;""" % (
        connection.escape(r['username'])))
    rows = cursor.fetchall()
    if rows != ():
        user = rows[0]
        if verify_password(user[1], r["password"]):
            session["user"] = {"name": user[0], "pass": user[1]}
            print(session["user"])
        else:
            return rend("login.html", code=1)
    else:
        print(rows)
        return rend("login.html", code=1)
    return redirect(url_for("index"))


@app.route("/account")
def account():
    if "user" in session.keys():
        if session["user"]["name"] != None:
            return rend("account.html", user=session["user"])
    return index()


@app.route("/logout")
def logout():
    session["user"] = {"name": None, "pass": None}
    return index()


if __name__ == '__main__':
    app.run()
