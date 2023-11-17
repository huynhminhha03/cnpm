from flask import Flask, render_template, request , redirect
from app import app, login
import datetime
from flask_login import login_user
import dao

@login.user_loader
def load_benhnhan(benhnhan_id):
    return dao.get_benhnhan_by_id(benhnhan_id)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
