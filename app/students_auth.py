import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('student_auth', __name__, url_prefix='/students/auth')

@bp.before_app_request
def load_logged_in_user():
    account_id = session.get('student_id')

    if account_id is None:
        g.student = None
    else:
        g.student = get_db().execute(
            'SELECT * FROM students WHERE id = ?', (account_id,)
        ).fetchone()

@bp.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        db = get_db()
        error = None
        student = db.execute(
            'SELECT * FROM students WHERE student_id = ?', (student_id,)
        ).fetchone()

        if student is None:
            error = 'No account found!'
        elif not check_password_hash(student['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session['student_id'] = student['id']
            redirect_url = session.get('redirect')
            if redirect_url is not None:
                del session['redirect']
                return redirect(redirect_url)
            else:
                return redirect(url_for('students.index'))

        flash(error,'error')
    else:
        redirect_url = request.args.get('redirect')
        if redirect_url is not None:
            session['redirect'] = redirect_url
    return render_template('students/index.html.jinja')

@bp.route('/logout')
def logout():
    session.pop('student_id')
    return redirect(url_for('students.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.student is None:
            return redirect(url_for('student_auth.login'))

        return view(**kwargs)

    return wrapped_view