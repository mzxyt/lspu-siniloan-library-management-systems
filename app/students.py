from string import whitespace
import sys
from unicodedata import category
from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


from app.students_auth import login_required
from app.db import get_db

bp = Blueprint('students', __name__)

def flash_error_msg(msg=None):
    if msg is None:
        msg = "System error, please try again!"
    
    return flash(msg, 'error')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@bp.route("/")
def index():
    db = get_db()
    categories = db.execute('SELECT * FROM categories').fetchall()
    return render_template('students/home.html.jinja',categories=categories)


@bp.route("/search")
def search_books():
    db = get_db()

    search_query = request.args.get('search_query')
    category = request.args.get("category")

    if search_query is None:
        search_query=""
    books = None
    
    
    categories = db.execute("SELECT * FROM categories").fetchall()
    selected_category = None
    
    if category is not None or category is not whitespace:
        selected_category = db.execute("SELECT * FROM categories WHERE name = ? ",(category,)).fetchone()
        
    if selected_category is not None and categories is not None:
        books = db.execute("SELECT books.copies, STRFTIME('%m-%d-%Y',books.date_published) as date, books.id,books.category_id,books.author_id,books.title,books.sypnosis, categories.name as category_name, authors.name as author_name FROM books INNER JOIN categories ON books.category_id = categories.id INNER JOIN authors ON books.author_id = authors.id WHERE (books.title LIKE ? OR books.sypnosis LIKE ?) AND books.category_id = ?",(f"%{search_query}%",f"%{search_query}%",selected_category['id'])).fetchall()
    else:
        books = db.execute("SELECT books.copies, STRFTIME('%m-%d-%Y',books.date_published) as date, books.id,books.category_id,books.author_id,books.title,books.sypnosis, categories.name as category_name, authors.name as author_name FROM books INNER JOIN categories ON books.category_id = categories.id INNER JOIN authors ON books.author_id = authors.id WHERE (books.title LIKE ? OR books.sypnosis LIKE ?) ",(f"%{search_query}%",f"%{search_query}%",)).fetchall()
    all_books=[]
    books_count = 0
    for book in books:
        borrowed = db.execute("SELECT COUNT(*) as count FROM rental_details INNER JOIN rentals ON rental_details.id = rentals.id WHERE rentals.status != 1 AND rentals.status != 3 AND rental_details.book_id = ?", (book['id'],)).fetchone()['count']
        new_book = {**book, 'available':book['copies'] - borrowed}
        books_count += book['copies'] - borrowed
        all_books.append(new_book)
    

    return render_template('students/search.html.jinja',books=books,search_query=search_query,result_count=len(books),books_count=books_count,categories=categories,selected_category=selected_category)

@bp.route('/borrow')
def borrow_book():
    db = get_db()

    if g.student is None:
        session['redirect'] = url_for('students.checkout')
        return redirect(url_for('student_auth.login') + "?redirect=" + url_for('students.checkout'))
    
    return redirect(url_for('students.checkout'))
   

@bp.route('/borrow/add',methods=('POST',))
def add_book():
    db = get_db()
    id = request.form['id']

    list = session.get('borrowed_books')

    if list is None or len(list) == 0:
        list = id
    else:
        list += ","+id

    session['borrowed_books'] = list

    return jsonify({'msg':'Successfully added','books':list})

@bp.route('/borrow/remove',methods=('POST',))
def remove_book():
    db = get_db()
    id = request.form['id']

    list = session.get('borrowed_books')
    list = str.split(list,',')

    list.remove(id);
    list_str = ","
    if len(list) > 1:
        list_str.join(list)
    elif len(list) == 1 and list != ",":
        list_str = list[0]
    else:
        list_str = ""

    session['borrowed_books'] = list_str

    return jsonify({'msg':'Successfully removed','books':list_str})

@bp.route('/borrow/get',methods=('POST',))
def get_selected_books():
    db = get_db()

    list = session.get('borrowed_books',None) #string : '1,2,3,4'

    if list is not None and len(list) > 0:
        books = db.execute("SELECT books.id, books.title, STRFTIME('%m-%d-%Y',books.date_published) as date, categories.name as category_name FROM books INNER JOIN categories ON books.category_id = categories.id WHERE books.id IN ("+list+")").fetchall()
        all_books = []

        for book in books:
            b = {
            'title':book['title'],
            'id':book['id'],
            'date_published':book['date'],
            'category_name':book['category_name'],
            } 
            all_books.append(b)

        return jsonify({
            'count':len(books),
            'books':all_books
        })
    else:
        return jsonify({
            'books':[],
            'msg':'No session'
        })

@bp.route('/checkout',methods=('POST','GET'))
@login_required
def checkout():
    db=get_db()

    if request.method == "POST":
        book_ids = request.form.getlist('book_id[]')
        student_id = request.form['student_id']
        
        try:
            get_id = db.execute("SELECT max(id) as id FROM rentals").fetchone()
            if get_id is None:
                last_id = 1
            else:
                if get_id['id']:
                    last_id = get_id['id'] + 1
                else:
                    last_id = 1
            rental_no = "LSPU-" + str(last_id).zfill(4)
            db.execute("INSERT INTO rentals(student_id, status,rental_no) VALUES(?,?,?)",(student_id,0,rental_no))
            db.commit()
            rental_id = db.execute("SELECT last_insert_rowid() as id FROM rentals").fetchone()['id']

            for book_id in book_ids:
                db.execute("INSERT INTO rental_details(rental_id,book_id) VALUES(?,?)",(rental_id,book_id))
                db.commit()
        except db.IntegrityError:
            flash_error_msg()
        else:
            # remove selected books from session after submitting requests
            del session['borrowed_books']
            return redirect(url_for('students.requests'))
        
    list = session.get('borrowed_books')
    books = []

    if list is not None:
        books = db.execute( "SELECT books.id, books.title, STRFTIME('%m-%d-%Y',books.date_published) as date, categories.name as category_name FROM books INNER JOIN categories ON books.category_id = categories.id WHERE books.id IN ("+list+")").fetchall()
    
    return render_template('students/checkout.html.jinja',books=books,books_count=len(books))

# requests
@bp.route('/requests')
@login_required
def requests():
    db=get_db()
    tabs = {'pending':0,'approved':1,'unreturned':2,'completed':3}
    tab = request.args.get('tab') if request.args.get('tab') else "pending"
    tab = tab.lower()

    student_id = g.student['id']
    requests = db.execute("SELECT students.*, rentals.status,rentals.rental_no,rentals.id as rental_id, STRFTIME('%m-%d-%Y',rentals.date_rented) as date FROM rentals INNER JOIN students ON rentals.student_id = students.id WHERE rentals.student_id=? AND rentals.status=? ORDER BY rentals.id DESC, rentals.status ASC",(student_id,tabs[tab])).fetchall()
    all_requests = []
    rental_details = []
    for req in requests:
        details = db.execute("SELECT rental_details.*,books.title,categories.name as category_name FROM rental_details INNER JOIN books ON rental_details.book_id = books.id INNER JOIN categories ON books.category_id = categories.id WHERE rental_details.rental_id = ?",(req['rental_id'],)).fetchall()
        new_request = {
            **req,
            "rental_details":details
        }
        all_requests.append(new_request)
        rental_details.append(details)

    total_requests = db.execute("SELECT COUNT(*) as count FROM rentals WHERE student_id=?",(student_id,)).fetchone()['count']
    unreturned = db.execute("SELECT COUNT(*) as count FROM rentals WHERE status != 0 AND status != 3 AND student_id=?",(student_id,)).fetchone()['count']
    pending = db.execute("SELECT COUNT(*) as count FROM rentals WHERE status = 0 AND student_id=?",(student_id,)).fetchone()['count']
    approved = db.execute("SELECT COUNT(*) as count FROM rentals WHERE status = 1 AND student_id=?",(student_id,)).fetchone()['count']
    completed = db.execute("SELECT COUNT(*) as count FROM rentals WHERE status = 3 AND student_id=?",(student_id,)).fetchone()['count']
    
    return render_template("students/requests.html.jinja",requests=all_requests,len=len(requests),rental_details=rental_details,tab=tab,total_requests=total_requests,unreturned=unreturned,pending=pending,approved=approved,completed=completed)

# returns json
@bp.route('/requests/get',methods=('POST',))
def get_request():
    db=get_db()
    db.row_factory = dict_factory
    id = request.form['id']

    req = db.execute("SELECT STRFTIME('%m-%d-%Y',date_rented) as date,id, rental_no FROM rentals WHERE id = ?",(id,)).fetchone()
    details = db.execute("SELECT rental_details.*,books.title,STRFTIME('%m-%d-%Y',books.date_published) as date, categories.name as category_name FROM rental_details INNER JOIN books ON rental_details.book_id = books.id INNER JOIN categories ON books.category_id = categories.id WHERE rental_details.rental_id = ?",(req['id'],)).fetchall()
    new_req = {**req, 'details':details }

    return jsonify(new_req)
    
@bp.route("/requests/delete")
def delete_request():
    db=get_db()
    id = request.args.get('id')

    try:
        db.execute("DELETE FROM rentals WHERE id = ?",(id,))
        db.commit()
    except:
        flash_error_msg()
    else:
        flash("Successfully removed request!")
    
    return redirect(url_for("students.requests"))

@bp.route("/profile",methods=('GET','POST'))
@login_required
def profile():
    if request.method == "POST":
        id = request.form['id']
        email = request.form['email']
        password = request.form.get('password',None)

        try:
            db = get_db()
            if password:
                db.execute("UPDATE students SET email = ?, password=? WHERE id = ?",(email, generate_password_hash(password),id))
                db.commit()
            else:
                db.execute("UPDATE students SET email = ? WHERE id = ?",(email, id))
                db.commit()
        except:
            flash_error_msg()
        else:
            flash("Successfully updated!")
    db=get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?",(g.student['id'],)).fetchone()
    return render_template("students/profile.html.jinja",account=student)

@bp.route('/profile/photo',methods=('POST','GET'))
def update_photo():
    photo = request.files['photo']
    id = request.form['id']
    # upload photo
    filename = secure_filename(photo.filename)
    path = 'static/images/' + filename
    photo.save("app/"+path)

    try:
        db=get_db()

        db.execute("UPDATE students SET photo = ? WHERE id=?",(path,id)).fetchone()
        db.commit()
    except:
        flash_error_msg()
    else:
        flash("Successfully updated!")
    return redirect(url_for("students.profile"))
