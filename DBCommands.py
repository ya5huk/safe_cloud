from datetime import datetime
import sqlite3

from DBObjects import DBFile, DBUser

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.db_con = sqlite3.connect(db_file_path, check_same_thread=False)
        self.cur = self.db_con.cursor() # Will be used to operate in db
    
    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS files
        (file_id text primary key, in_dir integer, name text, content blob, added_date text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
        (user_id text primary key, username text, email text, creation_date text, files text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS dirs
        (dir_id text primary key, name text, files text)''')
        
        self.db_con.commit()
        
    # Files
    
    def add_file(self, file: DBFile):
        self.cur.execute(f'''INSERT INTO files(file_id, in_dir, name, content, added_date)
        values (?, ?, ?, ?, ?)''',
        (file.file_id, '1' if file.in_dir else '0', file.name, file.content, str(file.added_date.strftime("%d/%m/%Y, %H:%M:%S"))))
        self.db_con.commit()

    def remove_file(self, filename: str):
        self.cur.execute(f'''DELETE FROM files WHERE name=:filename''', {'filename': filename})
        self.db_con.commit()
    
    def get_file_content(self, filename: str):
        self.cur.execute(f'''SELECT content FROM files WHERE name=:filename''', {'filename': filename})
        ans = self.cur.fetchall()
        if len(ans) == 0:
            return None
        content = ans[0][0] # If more than a file popps up, that is a problem
        return content # Bytes of the file
        
    # Users

    def add_user(self, usr: DBUser):
        self.cur.execute(f'''INSERT INTO users(user_id, username, email, creation_date, files)
        values (?, ?, ?, ?, ?)''',
        (usr.user_id,usr.username, usr.email, str(usr.creation_date.strftime("%d/%m/%Y, %H:%M:%S")), ','.join(usr.files)))
        self.db_con.commit()
    
    def remove_user_by_username(self, username: str):
        self.cur.execute(f'''DELETE FROM users WHERE username=:username''', {'username': username})
        self.db_con.commit()

    def remove_user_by_id(self, id: str):
        self.cur.execute(f'''DELETE FROM users WHERE user_id=:id''', {'id': id})
        self.db_con.commit()

    def get_user_details_by_value(self, value: str, input_type: str):
        if input_type not in ['user_id', 'username', 'email']:
            # You can find user only with those value types
            return None
        
        # command based on given type
        fetch_command = f'''SELECT * FROM users WHERE {input_type}=:{input_type}'''
        self.cur.execute(fetch_command, {input_type: value})
        ans = self.cur.fetchall()
        if len(ans) == 0:
            return None

        user = ans[0] # Should be only one user
        userid, username, email, creation_date, files = user # Splitting the tuple
        return DBUser(userid, username, email, datetime.strptime(creation_date, "%d/%m/%Y, %H:%M:%S"), files.split(','))
        

    def check_email_existance(self, email: str):
        self.cur.execute(f'''SELECT * FROM users WHERE email=:email''', {'email': email})
        ans = self.cur.fetchall()
        if len(ans) == 0: # empty list = no accounts
            return False
        return True
    

    def close(self):
        self.cur.close()

    def __repr__(self) -> str:
        return f'db api for -> {self.db_file_path}'
        

if __name__ == "__main__":
    db = DBCommands('./database.db')
    db.create_tables()
    print(db.get_user_details_by_value('838193d357558069ea86dd58135001517cd0c462d6b32bb830f96d06a980fa83', 'user_id'))
    