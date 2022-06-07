from flask import Flask, jsonify, redirect, url_for, render_template, request as rq
from CloudServer import CloudServer
import hashlib 
import re, os

DB_FILENAME = os.path.abspath('./database.db')
EXTENSION_ICONS_PATH = os.path.abspath('./images/extension_icons') + '/'

app = Flask(__name__)
cs = CloudServer(DB_FILENAME, EXTENSION_ICONS_PATH)
filenames = [] # All the user's filenames (should be fetched on load and updated)

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if rq.method == 'POST':
        email = rq.form['email']
        username = rq.form['username']
        password = rq.form['password']
        user_id = hashify_user(email, username, password)
        
        ans = cs.try_register(user_id, username, email)
        if ans['code'] == 'success':
            # Create a database
            return redirect(url_for('login'))
        else:
            
            return render_template('register.html', err_msg=ans['msg'])

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if rq.method == 'POST':
        usr_input = rq.form['user_input']
        usr_pass = rq.form['password']
    
    return render_template('login.html')
    

@app.route('/files', methods=['POST', 'GET'])
def files():
    
    if rq.method == 'POST':
        
        file = rq.files['file']
        content = file.stream.read()  # Send stream over a socket

        # Code to manage duplicated files 

        # Splitting filename.ext to filename, ext
        saved_filename = file.filename
        actual_name = '.'.join(saved_filename.split('.')[:-1])
        ext = saved_filename.split('.')[-1]
        
        # Adding (duplicated file number) if needed
        if saved_filename not in filenames:
            filenames.append(file.filename)
        else:
            # turn name.ext -> name (counter).ext
            occurrences = 0
            for filename in filenames:
                # we want to count 'filename' and 'filename (1)' for example
                # so filenames.count is not enough (we won't count the duplicated ones) 
                # regex finds files with struct -> filename (num).ext
                if re.match(f'{actual_name}.* \(\d*\).{ext}', filename) != None or filename == file.filename:
                    occurrences += 1
            
            saved_filename = f'{actual_name} ({occurrences}).{ext}'
            filenames.append(saved_filename)
        
        file_icon_data = cs.add_file(False, saved_filename, content)
        
        return jsonify({'data': file_icon_data.decode(), 'filename': saved_filename})

    return render_template('files.html')

@app.route('/files/download/<filename>')
def download_file(filename: str):
    content = cs.return_file_content(filename)
    return content

@app.route('/files/delete/<filename>')
def delete_file(filename: str):
    cs.delete_file(filename)
    filenames.remove(filename)
    # Doesn't really matter if we didn't delete something that didn't exist
    return jsonify({'message': 'Delete occurred'})

# TODO
# 1. Finish register and if success (no same emails!) redirect to login
# 2. In login, create sessions on successful login (permentant for 1 day)
#   a. Research about seesion secret key (should it be user id ?)
#   b. now add two-step auth with email
# 3. Connect now session to files tab so it will fetch all user files
# This is not only fetching but adding files / removing files
# must affect user's files list 
# 4. Add a profile page with all the needed details and LOG OUT button (important!)
# 5. Features: security - encrypt files and maybe decrypt with user-id, zip automatically files, trash section 

def hashify_user(email: str, username: str, password: str):
    # Using email because it is unique and password/username
    # for more unbreakable id
    mixed_str = username[::-2] + password[::-1] + email*5
    user_id = hashlib.sha256(mixed_str.encode()).hexdigest()
    return user_id

if __name__ == '__main__':
    app.run(debug=True)