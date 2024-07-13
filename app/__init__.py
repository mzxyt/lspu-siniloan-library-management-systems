import sqlite3
import os
from flask import Flask, render_template
from . import db



def create_app(test_config=None):
    app = Flask(__name__,  instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='!oujikhIY!*9nouioa',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    app.secret_key = app.config['SECRET_KEY']

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import admin_auth
    app.register_blueprint(admin_auth.bp)

    from . import students_auth
    app.register_blueprint(students_auth.bp)

    from . import students
    app.register_blueprint(students.bp)
    app.add_url_rule('/',endpoint="index")

    from . import admin
    app.register_blueprint(admin.bp)
    app.add_url_rule('/admin',endpoint="admin.dashboard")

    from . import api
    app.register_blueprint(api.bp)

    db.init_app(app)
    
    return app


def getDbConnection():
    return sqlite3.connect("library-system.db")