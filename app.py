from datetime import datetime, timedelta
from flask import Flask, jsonify, session, redirect, url_for, render_template, request as rq
from CloudServer import CloudServer
import CloudEncrypt 
import re, os

DB_FILENAME = os.path.abspath('./database.db')
EXTENSION_ICONS_PATH = os.path.abspath('./images/extension_icons') + '/'

app = Flask(__name__)
# Secret key
app.secret_key = 'dev' # Const in development
app.config.from_pyfile('config.py', silent=True) # Overrides if config.py exists

app.permanent_session_lifetime = timedelta(days=1)

cs = CloudServer(DB_FILENAME, EXTENSION_ICONS_PATH)
filenames = [] # All the user's filenames (should be fetched on load and updated)

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('files'))
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if rq.method == 'POST':
        email = rq.form['email']
        username = rq.form['username']
        password = rq.form['password']

        # The weird microsec cutting causes problems in login so I cut it
        creation_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        user_id = CloudEncrypt.hashify_user(email, password, datetime.strptime(creation_time, "%d/%m/%Y, %H:%M:%S"))
        
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
        ans = cs.try_login(usr_input, usr_pass)
        if ans['code'] == 'error':
            return render_template('login.html', err_msg=ans['msg'])
        else:
            # success
            session.permanent = True
            session['user_id'] = ans['msg'] 
            return redirect(url_for('files'))
    
    return render_template('login.html')
    

@app.route('/files', methods=['POST', 'GET'])
def files():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if rq.method == 'GET':
        # Fetch user's files 
        user_id = session['user_id']
        filenames = cs.get_user_filenames(user_id)
        
        files_data = []

        for fn in filenames:
            icon_content = b'data:image/png;base64,' + cs.get_file_icon_content(fn)
            files_data.append(
                {'name': fn,
                'icon_data': icon_content.decode()})
        return render_template('files.html', files_data=files_data)

    if rq.method == 'POST':
        
        file = rq.files['file']
        content = file.stream.read()  # Send stream over a socket

        return 'hello'
        # Code to manage duplicated files 

        # # Splitting filename.ext to filename, ext
        # saved_filename = file.filename
        # actual_name = '.'.join(saved_filename.split('.')[:-1])
        # ext = saved_filename.split('.')[-1]
        
        # # Adding (duplicated file number) if needed
        # if saved_filename not in filenames:
        #     filenames.append(file.filename)
        # else:
        #     # turn name.ext -> name (counter).ext
        #     occurrences = 0
        #     for filename in filenames:
        #         # we want to count 'filename' and 'filename (1)' for example
        #         # so filenames.count is not enough (we won't count the duplicated ones) 
        #         # regex finds files with struct -> filename (num).ext
        #         if re.match(f'{actual_name}.* \(\d*\).{ext}', filename) != None or filename == file.filename:
        #             occurrences += 1
            
        saved_filename = f'{actual_name} ({occurrences}).{ext}'
        filenames.append(saved_filename)
        
        file_icon_data = cs.add_file(False, saved_filename, content)
        
        return jsonify({'data': file_icon_data.decode(), 'filename': saved_filename})


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

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
    return redirect(url_for('login'))

# TODO
# 2. In login, create sessions on successful login (permentant for 1 day)
#   a. Research about session secret key (should it be user id ?)
#   b. now add two-step auth with email
# 3. Connect now session to files tab so it will fetch all user files
# This is not only fetching but adding files / removing files
# must affect user's files list 
# 4. Add a profile page with all the needed details and LOG OUT button (important!)
# 5. Features: security - encrypt files and maybe decrypt with user-id, zip automatically files, trash section 


    

if __name__ == '__main__':
    app.run(debug=True)