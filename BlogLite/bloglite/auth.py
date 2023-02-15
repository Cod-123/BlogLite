from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("You have succesfully logged in to your account!", category='success')
                #remembers and acts as asession for user login
                
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect credentials ! Provide the corect details.', category='error')
        else:
            flash('Email does not exist. Please proveid a valid one', category='error')

    return render_template("login.html",user=current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        pwd1 = request.form.get("password1")
        pwd2 = request.form.get("password2")

        curr_email = User.query.filter_by(email=email).first()
        curr_user = User.query.filter_by(username=username).first()

        if curr_user:
            flash('Username already exists.. Please choose a different one', category='error')

        elif curr_email:
           flash('Email already exists..Choose a different one', category='error')

        elif len(username) < 3:
            flash('Username is too short.Please choose a valid length username', category='error')

        elif pwd1 != pwd2:
            flash('Passwords do not match!', category='error')

        elif len(email) < 5:
            flash("Email is invalid.", category='error')

        elif len(pwd1) < 6:
            flash('Password is too short.Please choose a valid length password', category='error')
       
        else:
            #create new user
            new_user = User(username=username,email=email,password=generate_password_hash(pwd1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Your account has been created succesfully!')
            return redirect(url_for('views.home'))

    return render_template("signup.html",user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

