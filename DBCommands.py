import sqlite3

from DBObjects import DBFile

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.db_con = sqlite3.connect(db_file_path)
        self.cur = self.db_con.cursor() # Will be used to operate in db
    
    def create_tables(self):
        self.cur.execute('''CREATE TABLE files
        (file_id integer primary key autoincrement, in_dir integer, name text, content blob, added_date text)''')

        # ...
        self.cur.commit()
    
    def add_file(self, file: DBFile):
        self.cur.execute(f'''INSERT INTO files
        ({file.file_id}, {file.in_dir}, {file.name}, {file.content}, {str(file.added_date)})''')

    def close(self):
        self.cur.close()

if __name__ == "__main__":
    db = DBCommands()
    db