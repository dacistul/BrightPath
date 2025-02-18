from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import re
from flask_babel import gettext as _

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            translated_account_type = _('Professor') if user.account_type == 'professor' else _('Student')
            if check_password_hash(user.password, password):
                flash(_('Logged in successfully as %(account_type)s!', account_type=translated_account_type), category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash(_('Incorrect password, try again.'), category='error')
        else:
            flash(_('User does not exist.'), category='error')

    return render_template("login.html", user=current_user)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get('email')
        account_type = request.form.get('account_type') #stud/prof

        user = User.query.filter_by(username=username).first()

        if user:
            flash(_('User already exists. Log in!'), category='error')
        elif len(username) < 3:
            flash(_('Username must be greater than 3 characters'), category='error')
        elif len(password) < 3:
            flash(_('Password must be greater than 3 characters'), category='error')
        elif password != repassword:
            flash(__build_class__('Passwords must match'), category='error')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|ro)$', email):
            flash(_('Invalid email format. Please use a valid email (e.g., example@domain.com or example@domain.ro).'), category='error')
        else:
            #add user to database
            new_user = User(email=email, username=username, password=generate_password_hash(password), account_type=account_type)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(_('Account was created'), category='success')
            return redirect(url_for('views.home'))
            
    return render_template("signup.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))