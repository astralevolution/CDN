import os
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COUNTER_FILE'] = 'counter.txt'
app.config['MAX_FILE_SIZE'] = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
  return True  # Allow any file extension


def get_counter():
  counter = 0
  counter_file = app.config['COUNTER_FILE']

  if os.path.exists(counter_file):
    with open(counter_file, 'r') as file:
      counter = int(file.read())

  return counter


def update_counter(counter):
  counter_file = app.config['COUNTER_FILE']

  with open(counter_file, 'w') as file:
    file.write(str(counter))


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
    return render_template('upload_error.html', error='No file part'), 400

  file = request.files['file']

  if file.filename == '':
    return render_template('upload_error.html', error='No selected file'), 400

  if file:
    if request.content_length > app.config['MAX_FILE_SIZE']:
      return render_template('upload_error.html', error='File size exceeds 10MB'), 400
      print("File exceeds 10MB")

    counter = get_counter()
    counter += 1
    update_counter(counter)

    filename = f'file_{counter}.{file.filename.rsplit(".", 1)[1]}'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    file_url = f'https://cdn.astralevolution.pro/{file_path}'  # Modify this URL as needed
    return render_template('upload_success.html', file_url=file_url)

  return render_template('upload_error.html', error='Invalid file'), 400


@app.route('/uploads/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
  if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
  app.run(host='0.0.0.0', port=3000)
