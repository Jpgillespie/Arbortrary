from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User 

@app.route('/')
def register_user():
    if 'user' not in session:
        return render_template('login_register.html')
    else:
        return redirect('/dashboard')

@app.route('/user/login', methods = ["POST"])
def user_login():
    user = User.login_user(request.form)
    if not user:
        return redirect('/')
    session['user'] = user.__dict__
    return redirect('/dashboard')


@app.route('/user/logout', methods = ["GET"])
def user_logout():
    del session['user']
    return redirect("/")


@app.route('/user/register', methods = ["POST"])
def user_register():
    if not User.validate_registration(request.form):
        return redirect('/')
    lastRowId = User.create_user(request.form)
    user = User.get_user_by_id(lastRowId)
    session['user'] = user.__dict__
    return redirect('/')