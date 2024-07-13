from distutils.log import error
import functools

from flask import (
    Blueprint, flash, g, jsonify, make_response, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@bp.route('/books', methods=('POST',))
def get_books():
    if(request.method == "POST"):
        id = request.form['id']
        db = get_db()

        book = db.execute("SELECT STRFTIME('%m-%d-%Y',books.date_published) as date, books.id,books.category_id,books.author_id,books.title,books.sypnosis, categories.name as category_name, authors.name as author_name FROM books INNER JOIN categories ON books.category_id = categories.id INNER JOIN authors ON books.author_id = authors.id WHERE books.id = ?",(id,)).fetchone()

        return make_response(
            jsonify({
            'title':book['title'],
            'id':book['id'],
            'sypnosis':book['sypnosis'],
            'date_published':book['date'],
            'category_id':book['category_id'],
            'author_id':book['author_id'],
            'category_name':book['category_name'],
            'author_name':book['author_name'],
        })
        )

@bp.route('/requests/get',methods=('POST',))
def get_request():
    db=get_db()
    db.row_factory = dict_factory
    id = request.form['id']

    req = db.execute("SELECT students.firstname, students.lastname, students.year_level, STRFTIME('%m-%d-%Y',rentals.date_rented) as date,rentals.id, rentals.rental_no FROM rentals INNER JOIN students ON rentals.student_id = students.id WHERE rentals.id = ?",(id,)).fetchone()
    details = db.execute("SELECT rental_details.*,books.title,STRFTIME('%m-%d-%Y',books.date_published) as date, categories.name as category_name FROM rental_details INNER JOIN books ON rental_details.book_id = books.id INNER JOIN categories ON books.category_id = categories.id WHERE rental_details.rental_id = ?",(req['id'],)).fetchall()
    new_req = {**req, 'details':details }

    return jsonify(new_req)

# @bp.route('/requests/update/status',methods=('POST',))
# def update_request_status():
#     db=get_db()
    

@bp.route('/students/password/check',methods=('POST',))
def check_student_password():
    db=get_db()
    id = request.form['id']
    password = request.form['password']
    student = db.execute("SELECT * FROM students WHERE id = ?",(id,)).fetchone()

    matched = check_password_hash(student['password'],password)

    return jsonify({
        'matched':matched
    })

@bp.route('/admin/password/check',methods=('POST',))
def check_admin_password():
    db=get_db()
    id = request.form['id']
    password = request.form['password']
    admin = db.execute("SELECT * FROM admin WHERE id = ?",(id,)).fetchone()

    matched = check_password_hash(admin['password'],password)

    return jsonify({
        'matched':matched
    })

