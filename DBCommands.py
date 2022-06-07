from datetime import datetime
import sqlite3

from DBObjects import DBFile, DBUser

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.db_con = sqlite3.connect(db_file_path)
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
        content = self.cur.fetchall()[0][0] # If more than a file popps up, that is a problem
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

    def get_user_details_by_id(self, id: str):
        self.cur.execute(f'''SELECT * FROM users WHERE user_id=:id''', {'id': id})
        user = self.cur.fetchall()[0] # Should be only one user
        userid, username, email, creation_date, files = user # Splitting the tuple
        return DBUser(id, username, email, datetime.strptime(creation_date, "%d/%m/%Y, %H:%M:%S"), files.split(','))
        

    def close(self):
        self.cur.close()

    def __repr__(self) -> str:
        return f'db api for -> {self.db_file_path}'
        

if __name__ == "__main__":
    db = DBCommands('./user.db')
    db.create_tables()
    id = '1156a4sdf'
    usr = db.get_user_details_by_id(id)
    newUsr = usr
    newUsr.user_id = 'asdadsf'
    newUsr.username = 'topo'
    db.remove_user_by_username('topo')
    print(usr.creation_date, usr.email, usr.files, usr.user_id, usr.username)
    