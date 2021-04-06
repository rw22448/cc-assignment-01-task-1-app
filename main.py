import datetime

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from google.cloud import datastore, storage
from localStoragePy import localStoragePy

app = Flask(__name__)

datastore_client = datastore.Client()
storage_client = storage.Client()
localStorage = localStoragePy('cc-assignment-01-task-1-app', 'text')


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    users = fetch_users()
    error = None

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        for user in users:
            if id == user['id']:
                if password == user['password']:
                    localStorage.setItem('user_id', user['id'])
                    return redirect(url_for('forum'))
                else:
                    error = 'ID or password is invalid'
            else:
                error = 'ID or password is invalid'

    return render_template('login.html', error=error)


@app.route('/register', methods=('GET', 'POST'))
def register():
    users = fetch_users()
    error = None

    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        image = request.files['image']

        for user in users:
            if id == user['id']:
                error = 'The ID already exists'

        for user in users:
            if username == user['user_name']:
                error = 'The username already exists'

        if error is None:
            upload_image(
                image, 'cc-assignment-01-task-1-app.appspot.com', id)

            store_user(id, username, password)
            return redirect(url_for('login'))

    return render_template('register.html', error=error)


@app.route('/forum', methods=('GET', 'POST'))
def forum():
    if not localStorage.getItem('user_id'):
        return redirect(url_for('login'))

    user_id = localStorage.getItem('user_id')
    posts = fetch_posts(10)

    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        image = request.files['image']
        filename = secure_filename(image.filename)
        current_datetime = datetime.datetime.now()

        store_post(subject, message, subject +
                   filename, current_datetime, user_id)
        upload_image(
            image, 'cc-assignment-01-task-1-app-message-images', subject + filename)

    return render_template('forum.html', user_id=user_id, posts=posts)


@app.route('/user-page')
def user_page():

    return render_template('user_page.html')


@app.route('/logout')
def logout():
    localStorage.removeItem('user_id')

    return redirect(url_for('login'))


def fetch_users(limit=None):
    query = datastore_client.query(kind='user')
    query.order = ['id']

    output = query.fetch(limit=limit)

    return list(output)


def fetch_posts(limit=None):
    query = datastore_client.query(kind='post')
    query.order = ['-datetime']

    output = query.fetch(limit=limit)

    return list(output)


def store_user(id, username, password):
    entity = datastore.Entity(key=datastore_client.key('user'))
    entity.update({
        'id': id,
        'user_name': username,
        'password': password
    })

    datastore_client.put(entity)


def store_post(subject, message, image_id, current_datetime, user_id):
    entity = datastore.Entity(key=datastore_client.key('post'))
    entity.update({
        'subject': subject,
        'message': message,
        'image_id': image_id,
        'datetime': current_datetime,
        'user_id': user_id
    })

    datastore_client.put(entity)


def upload_image(file, bucket, blob):
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(blob)
    blob.upload_from_file(file)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
