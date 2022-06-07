from datetime import datetime
import json
from DBCommands import DBCommands
from DBObjects import DBFile, DBUser
import uuid
import base64
from IconGrabber import IconGrabber

class Codes:
    ADD_FILE = '101'
    GET_FILE_CONTENT = '102'
    DELETE_FILE = '103'

    REGISTER_USER = '201'

MAX_FILENAME_SIZE = 50

class CloudServer:
    def __init__(self, db_filename: str, extension_icons_path: str):
        self.db = DBCommands(db_filename)
        self.db.create_tables() # Doesn't do anything if exists
        self.icon_grabber = IconGrabber(extension_icons_path)

    # Fucntion adds a file to database and returns it's supposed icon in base64
    def add_file(self, in_dir: bool, filename: str, content: bytes):
        file_id = str(uuid.uuid1()) # By timestamp
        creation_time = datetime.now()      
        file = DBFile(file_id, in_dir, filename, content, creation_time)
        
        print('Adding file: ', file)
        self.db.add_file(file)

        # After file is added, send back the icon to the client
        # so website will show file's added icon
        
        icon_filepath = self.icon_grabber.grab_filepath(filename)

        with open(icon_filepath, 'rb') as f:
            icon_content = f.read()
        
        return base64.b64encode(icon_content)
        
    # Function returns file base64 content based on filename 
    def return_file_content(self, filename: str):
        content = self.db.get_file_content(filename)
        if content == None:
            print("Didn't receive anything from file, should get an error")

        return base64.b64encode(content)

    # Function deletes file with a give filename
    def delete_file(self, filename: str):
        self.db.remove_file(filename)

    # Function tries to register a user and returns a msg accordingly
    def try_register(self, user_id: str, username: str, email: str):
        if self.db.check_email_existance(email): 
            print(email, 'already exists!')
            return {'code': 'fail', 'msg': f'{email} already exists!'}
        
        usr = DBUser(user_id, username, email, datetime.now(), [])
        self.db.add_user(usr)

        return {'code': 'success', 'msg': ''}


if __name__ == '__main__':
    cs = CloudServer('127.0.0.1', 8081)

