import sqlite3

from DBObjects import DBFile

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.db_con = sqlite3.connect(db_file_path)
        self.cur = self.db_con.cursor() # Will be used to operate in db
    
    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS files
        (file_id text primary key, in_dir integer, name text, content blob, added_date text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
        (user_id text primary key, username text, email text, creation_date text, files text, dirs text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS dirs
        (dir_id text primary key, name text, files text)''')
        
        self.db_con.commit()
        
    
    def add_file(self, file: DBFile):
        self.cur.execute(f'''INSERT INTO files(file_id, in_dir, name, content, added_date)
        values (?, ?, ?, ?, ?)''',
        (file.file_id, '1' if file.in_dir else '0', file.name, file.content, str(file.added_date.strftime("%d/%m/%Y, %H:%M:%S"))))
        self.db_con.commit()

    def remove_file(self, file_id: str):
        self.cur.execute(f'''DELETE FROM files WHERE file_id == {file_id}''')
        self.db_con.commit()
    

    def close(self):
        self.cur.close()

    def __repr__(self) -> str:
        return f'db api for -> {self.db_file_path}'
        

if __name__ == "__main__":
    db = DBCommands()
    