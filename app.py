from flask import Flask, redirect, url_for, render_template, request as rq
from CloudServer import CloudClient
import io 

app = Flask(__name__)
cc = CloudClient('127.0.0.1', 8081)

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/files', methods=['POST', 'GET'])
def files():
    if rq.method == 'POST':
        
        file = rq.files['file']
        
        content = file.stream.read()  # Send stream over a socket
        cc.send_file(False, file.filename, content)
    return render_template('files.html')

if __name__ == '__main__':
    app.run(debug=True)