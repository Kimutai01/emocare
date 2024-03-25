#IMPORT SYSTEM FILES
from flask import Flask, render_template, request, redirect, url_for
from voice_auth import enroll, recognize



app = Flask(__name__)
name_given = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enroll', methods=['POST'])
def enroll_route():
    global name_given
    name = request.form['name']
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        temp_path = 'temp_upload.wav'
        uploaded_file.save(temp_path)
        result = enroll(name, temp_path)
        return render_template('index.html', result=name_given)
    else:
        return "No file uploaded for enrollment."

@app.route('/recognize', methods=['POST'])
def recognize_route():
    global name_given
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        temp_path = 'temp_upload.wav'
        uploaded_file.save(temp_path)
        result = recognize(temp_path)
        return render_template('index.html', result=name_given)
    else:
        return "No file uploaded for recognition."


if __name__ == '__main__':
    app.run(debug=True)

