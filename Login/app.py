from flask import url_for, session, Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "slkejfe"

ID = "choi"
PW = "wogud"

@app.route("/")
def home():
    if"userID" in session:
        return render_template("login.html", username = session.get("userID"), login=True)
    else:
        return render_template("login.html", login = False)


@app.route("/login", methods = ["GET"])
def login():
    _id_ = request.args.get("loginId")
    _password_ = request.args.get("loginPw")

    if ID== _id_ and PW == _password_:
        session["userID"] = _id_
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("userID")
    return redirect(url_for("home"))


app.run(host="0.0.0.0")