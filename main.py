import datetime

from flask import Flask, render_template, request, flash, redirect, url_for
from google.cloud import datastore

app = Flask(__name__)

datastore_client = datastore.Client()


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
            print(user)

            if id == user['id']:
                if password == user['password']:
                    return redirect(url_for('index'))
                else:
                    error = 'ID or password is invalid'
            else:
                error = 'ID or password is invalid'

    return render_template('login.html', error=error)


def fetch_users():
    query = datastore_client.query(kind='user')
    query.order = ['id']

    output = query.fetch()

    return list(output)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
