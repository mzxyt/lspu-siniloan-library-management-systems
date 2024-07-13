import functools
import os
from webbrowser import get

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.db import get_db

bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

@bp.before_app_request
def load_logged_in_user():
    account_id = session.get('admin_id')

    if account_id is None:
        g.admin = None
    else:
        g.admin = get_db().execute(
            'SELECT * FROM admin WHERE id = ?', (account_id,)
        ).fetchone()


# Route Signing up admin
@bp.route('/signup', methods=('GET','POST'))
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        photo = request.files['photo']
        name = request.form['name']
        db = get_db()
        
        error = None
        if error is None:
            filename = secure_filename(photo.filename)
            path = 'static/images/' + filename
            photo.save("app/"+path)
            
            try:
                db.execute(
                    'INSERT INTO admin(name,email,username,password,photo) VALUES(?,?,?,?,?)',(name,email,username,generate_password_hash(password),path)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Email {email} is already taken."

            else:
                flash('Successfully created an account.')
                return redirect(url_for("admin_auth.signin"))
        flash(error,'error')    
        
    else:
        db = get_db()
        admin = db.execute('SELECT COUNT(*) as count FROM admin').fetchone()

        if int(admin['count']) > 0:
            return redirect(url_for('admin_auth.signin'))
        else:
            return render_template('admin/auth/signup.html.jinja')
    return render_template('admin/auth/signup.html.jinja')


# Route for login
@bp.route('/signin',methods=('POST','GET'))
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()

        admin = db.execute(
            'SELECT * FROM admin WHERE username = ?',(username,)
        ).fetchone()
        
        error = None
        if admin is None:
            error = "Invalid sign in credentials!"
        elif not check_password_hash(admin['password'], password):
            error = "Incorrect Password!"

        if error is None:
            session['admin_id'] = admin['id']
            flash('Welcome admin!')
            return redirect(url_for('admin.dashboard'))
        flash(error,'error')    
    else:
        db = get_db()
        admin = db.execute('SELECT COUNT(*) as count FROM admin').fetchone()

        if int(admin['count']) <= 0:
            return redirect(url_for('admin_auth.signup'))

    return render_template('admin/auth/signin.html.jinja')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for('admin_auth.signin'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/signout')
def sign_out():
    g.admin = None
    del session['admin_id']
    return redirect('/admin')