from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import random
import string

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './'
app.config['MAX_FILE_SIZE'] = 25 * 1024 * 1024  # 10MB

port = 3000
def allowed_file(filename):
    return True

def generate_random_filename():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(16))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/style', methods=['GET'])
def style():
    return render_template('style.css')
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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

            file_url = f'https://cdn.trophyx.co/{filename}'
            return redirect(url_for('upload_success', file_url=file_url))

    return render_template('upload.html')

@app.route('/upload_success', methods=['GET'])
def upload_success():
    file_url = request.args.get('file_url')
    return render_template('upload_success.html', file_url=file_url)

@app.route('/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=port)
