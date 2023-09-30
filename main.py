import os
import random
import string
from flask import Flask, render_template, request, send_from_directory, session
import secrets
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = './'
app.config['MAX_FILE_SIZE'] = 10 * 1024 * 1024  # 10MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_random_filename():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(16))

def get_counter():
    counter = session.get('counter', 0)
    return counter

def update_counter(counter):
    session['counter'] = counter

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('uploaded_file'):
        return render_template('upload_success.html', file_url=session['uploaded_file'])

    if 'file' not in request.files:
        return render_template('upload_error.html', error='No file part'), 400

    file = request.files['file']

    if file.filename == '':
        return render_template('upload_error.html', error='No selected file'), 400

    if file:
        if request.content_length > app.config['MAX_FILE_SIZE']:
            return render_template('upload_error.html', error='File size exceeds 10MB'), 400

        if not allowed_file(file.filename):
            return render_template('upload_error.html', error='Invalid file type'), 400

        random_filename = generate_random_filename()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f'{random_filename}.{file_extension}'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_url = f'https://cdn.astralevolution.pro/{filename}'
        session['uploaded_file'] = file_url
        return render_template('upload_success.html', file_url=file_url)

    return render_template('upload_error.html', error='Invalid file'), 400

@app.route('/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=3000)
