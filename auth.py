from flask import Blueprint, render_template, url_for, redirect, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import *
from sqlalchemy.exc import IntegrityError

from flask_login import UserMixin, login_user, logout_user, login_required


auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup() :
    if request.method == 'POST' :
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        print(username, password)

        if not email or not username or not password:
            flash("All fields are required")
            return redirect(url_for('auth.signup'))

        try :
            user = User(email=email,
                        username=username,
                        password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))

        # IntegrityError - when a database operation violates a constraint such as UNIQUE, NOT NULL, or FOREIGN KEY
        except IntegrityError :         
            db.session.rollback()
            flash("Username or email already exists")
            return redirect(url_for('auth.signup'))
    


    return render_template("signup.html") 

@auth.route('/login', methods=['GET', 'POST'])
def login() :
    if request.method == 'POST' :
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        # Validate data before committing
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password) :
            # print(user, password)
            flash("invalid username or password")
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=bool(remember))
        return redirect(url_for('main.index'))

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout() :
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('auth.login'))

