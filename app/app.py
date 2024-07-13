import pyrebase
from flask import Flask, render_template, request

firebaseConfig = {
  "apiKey": "AIzaSyC-wgOaVsTWvyHKp1criJvRwv-Qs7000AI",
  "authDomain": "lspu-library.firebaseapp.com",
  "databaseURL": "https://lspu-library-default-rtdb.firebaseio.com",
  "projectId": "lspu-library",
  "storageBucket": "lspu-library.appspot.com",
  "messagingSenderId": "1017805405120",
  "appId": "1:1017805405120:web:412d94bb40663503772625",
  "measurementId": "G-R40HQ66G76"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def basic():
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            name = request.form['name']
            db.child("todo").push(name)
            todo = db.child("todo").get()
            to = todo.val()
            return render_template('index.html', t=to.values())
        elif request.form['submit'] == 'delete':
            db.child("todo").remove()
        return render_template('index.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
