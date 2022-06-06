from flask import Flask, jsonify, redirect, url_for, render_template, request as rq
from CloudServer import CloudClient
import io 

app = Flask(__name__)
cc = CloudClient('127.0.0.1', 8081)
filenames = [] # All the user's filenames (should be fetched on load and updated)

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
        
        # Code to manage duplicated files 
        saved_filename = file.filename
        if saved_filename not in filenames:
            filenames.append(file.filename)
        else:
            # turn name.ext -> name (counter).ext
            occurrences = filenames.count(file.filename)
            actual_name = '.'.join(saved_filename.split('.')[:-1])
            ext = saved_filename.split('.')[-1]
            saved_filename = f'{actual_name} ({occurrences}).{ext}'
        
        file_icon_data = cc.send_file(False, saved_filename, content)
        
        return jsonify({'data': file_icon_data.decode(), 'filename': saved_filename})

    return render_template('files.html')

@app.route('/files/download/<filename>')
def download_file(filename):
    cc.get


if __name__ == '__main__':
    app.run(debug=True)