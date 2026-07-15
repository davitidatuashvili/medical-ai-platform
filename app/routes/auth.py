from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select
from .. import db
from ..models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if len(name) < 2 or "@" not in email or len(password) < 6:
            flash("შეავსეთ ყველა ველი სწორად. პაროლი მინიმუმ 6 სიმბოლო.", "error")
            return render_template("register.html")

        existing = db.session.scalar(select(User).where(User.email == email))
        if existing:
            flash("ამ ელფოსტით მომხმარებელი უკვე არსებობს.", "error")
            return render_template("register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.scalar(select(User).where(User.email == email))

        if not user or not user.check_password(password):
            flash("ელფოსტა ან პაროლი არასწორია.", "error")
            return render_template("login.html")

        login_user(user, remember=True)
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
