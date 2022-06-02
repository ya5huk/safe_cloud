import sqlite3

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path