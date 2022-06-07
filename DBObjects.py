import datetime

class DBFile:
    def __init__(self, file_id: str, in_dir: bool, name: str, content: bytes, added_date: datetime.datetime):
        self.file_id = file_id
        self.in_dir = in_dir
        self.name = name
        self.content = content
        self.added_date = added_date

    def __repr__(self):
        return f'{self.file_id} -> {self.name}, {self.added_date}'

class DBUser:
    def __init__(self, user_id: str, username: str, email: str, creation_date: datetime.datetime, files: list[str]):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.creation_date = creation_date
        self.files = files
    
    def __repr__(self):
        return f'{self.user_id} -> {self.username} ({self.email})'