from contextlib import redirect_stderr
from datetime import datetime, timedelta
from flask import Flask, jsonify, session, redirect, url_for, render_template, request as rq
from CloudServer import CloudServer
from TwoStepAuth import TwoStepAuth
import CloudEncrypt 
import re, os

DB_FILENAME = os.path.abspath('./database.db')
EXTENSION_ICONS_PATH = os.path.abspath('./images/extension_icons') + '/'
tsa = TwoStepAuth('ilan147963@gmail.com')
auth_codes = [] # list of {email: code, email: code} used for 2step auth
# just to prevent it from be shared in session

app = Flask(__name__)
# Secret key
app.secret_key = 'dev' # Const in development
app.config.from_pyfile('config.py', silent=True) # Overrides if config.py exists

app.permanent_session_lifetime = timedelta(days=1)

cs = CloudServer(DB_FILENAME, EXTENSION_ICONS_PATH)

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

@app.route('/two-step-auth', methods=['POST', 'GET'])
def two_step_auth():
    if rq.method == 'POST':
        # If we received a POST req, then we already 
        # did a GET here, and values are popped
        # so this if must be first, to not get redirected
        recieved_code = rq.form['code_input']
        email = session.pop('email', None)
        redirect_to = session.pop('next_station', None)
        for ac in auth_codes:
            if ac['email'] == email and ac['code'] == recieved_code:
                # code that is typed is connected to the email
                # success
                auth_codes.remove(ac)

                session.permanent = True
                session['user_id'] = cs.get_user_details(email, 'email').user_id
                session['filenames'] = []
                return redirect(url_for(redirect_to))
        
        session['err_msg'] = "Wrong code, please try again."
        return redirect(url_for('login'))
    

    if 'email' not in session or 'next_station' not in session:
            return redirect(url_for('login'))

    email = session['email']
    redirect_to = session['next_station']
    code = tsa.generate_code(6)

    auth_codes.append({'email': email, 'code': code})
    
    if not tsa.check_if_email_exists(email):
        session['err_msg'] = 'Email does not exist!'
        session.pop('email', None) # Clear session
        session.pop('next_station', None)
        return redirect(url_for(redirect_to))
    
    tsa.send_code(code, email)

    return render_template('code_enter.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if rq.method == 'POST':
        usr_input = rq.form['user_input']
        usr_pass = rq.form['password']
        ans = cs.try_login(usr_input, usr_pass)
        if ans['code'] == 'error':
            return render_template('login.html', err_msg=ans['msg'])
        else:
            user = cs.get_user_details(ans['msg'], 'user_id')
            if not user:
                return render_template('login.html', err_msg='No such user..')
            session['email'] = user.email  # Where to send
            session['next_station'] = 'files'  # Where to redirect
            return redirect(url_for('two_step_auth'))
           
    err_msg = session.pop('err_msg', None)
    if err_msg:
        return render_template('login.html', err_msg=err_msg)
    return render_template('login.html')
    

@app.route('/files', methods=['POST', 'GET'])
def files():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if rq.method == 'GET':
        # Fetch user's files 
        user_id = session['user_id']
        filenames = cs.get_user_filenames(user_id)
        
        session['filenames'] = filenames
        
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

        # Manage duplicates
        saved_filename = configure_filename(file.filename, session['filenames'])
        file_id, file_icon_data = cs.add_file(False, saved_filename, content)
        
        # Update user's files
        cs.add_file_to_user(session['user_id'], file_id)


        return jsonify({'data': file_icon_data.decode(), 'filename': saved_filename})


@app.route('/files/download/<filename>')
def download_file(filename: str):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Search for filename among only the logged account
    files_id = cs.get_user_file_ids(session['user_id'])
    for fid in files_id:
        
        if cs.get_filename(fid) == filename:
            # Found relevant file, so I can download it 
            content = cs.return_file_content_by_id(fid)
            return content
    return redirect(url_for('login')) # If file wasn't found

@app.route('/files/delete/<filename>')
def delete_file(filename: str):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Search for filename among only the logged account
    files_id = cs.get_user_file_ids(session['user_id'])
    for fid in files_id:
        
        if cs.get_filename(fid) == filename:
            
            cs.delete_file_by_value(fid, 'file_id') # files
            cs.remove_file_from_user(session['user_id'], fid) # user
            session['filenames'].remove(filename) # session

            # Doesn't really matter if we didn't delete something that didn't exist
            return jsonify({'message': 'Delete occurred'})

    return redirect(url_for('login')) # No file found

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = cs.get_user_details(session['user_id'], 'user_id')
    if user:
        # Send in it parts because I don't want all the details
        # out there, sounds risky
        return render_template('profile.html',
        username=user.username,
        email=user.email,
        creation_date = user.creation_date.strftime("%d %B, %Y"),
        )
    return 'error'

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        session.pop('filenames', None)
    return redirect(url_for('login'))

# TODO
# 3. Add a profile page with all the needed details and LOG OUT button (important!)
# 4. Two-step auth
# 5. Navigation buttons everywhere (so I can move from login to register f.e)
# 6. Features: security - encrypt files and decrypt with user-id , zip automatically files, trash section 

def configure_filename(filename: str, curr_filenames: list[str]):
    saved_filename = filename
    actual_name = '.'.join(saved_filename.split('.')[:-1])
    ext = saved_filename.split('.')[-1]
    
    # Adding (duplicated file number) if needed
    if saved_filename not in curr_filenames:
        curr_filenames.append(filename)
    else:
        # turn name.ext -> name (counter).ext
        occurrences = 0
        for fn in curr_filenames:
            # we want to count 'filename' and 'filename (1)' for example
            # so filenames.count is not enough (we won't count the duplicated ones) 
            # regex finds files with struct -> filename (num).ext
            if re.match(f'{actual_name}.* \(\d*\).{ext}', filename) != None or fn == filename:
                occurrences += 1
        
        saved_filename = f'{actual_name} ({occurrences}).{ext}'

        curr_filenames.append(saved_filename)

    return saved_filename
    

if __name__ == '__main__':
    app.run(debug=True)