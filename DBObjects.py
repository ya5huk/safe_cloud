import datetime

class DBFile:
    def __init__(self, file_id: str, in_dir: bool, name: str, content: bytes, added_date: datetime.datetime):
        self.file_id = file_id
        self.in_dir = in_dir
        self.name = name
        self.content = content
        self.added_date = added_date

    # def to_dict(self):
    #     return {
            
    #         'in_dir': self.in_dir,
    #         'name': self.name,
    #         'content': self.content
    #     }
    
    def __repr__(self):
        return f'{self.file_id} -> {self.name}, {self.added_date}'