from datetime import datetime
import json
from DBCommands import DBCommands
from DBObjects import DBFile, DBUser
import uuid
import base64
from IconGrabber import IconGrabber
from CloudEncrypt import hashify_user
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
        
        return file_id, self.get_file_icon_content(filename)
        
    def get_file_icon_content(self, filename: str):
        icon_filepath = self.icon_grabber.grab_filepath(filename)

        with open(icon_filepath, 'rb') as f:
            icon_content = f.read()
        
        return base64.b64encode(icon_content)

    # Function returns file base64 content based on filename 
    def return_file_content_by_id(self, file_id: str):
        content = self.db.get_file_content(file_id)
        if content == None:
            print("Didn't receive anything from file, should get an error")

        return base64.b64encode(content)

    # Function deletes file with a give filename
    def delete_file_by_value(self, value: str, value_type: str):
        if value_type == 'file_id':
            self.db.remove_file_by_id(value)
        if value_type == 'filename':
            self.db.remove_file_by_name(value) 

    # Function tries to register a user and returns a msg accordingly
    def try_register(self, user_id: str, username: str, email: str):
        if self.db.check_email_existance(email): 
            print(email, 'already exists!')
            return {'code': 'errpr', 'msg': f'{email} already exists!'}
        
        usr = DBUser(user_id, username, email, datetime.now(), [])
        self.db.add_user(usr)

        return {'code': 'success', 'msg': ''}

    def try_login(self, usr_input: str, usr_pass: str):
        # User input may be email or username so we must check for both cases
        input_type = 'email'
        if not self.db.check_email_existance(usr_input): # email not exists
            input_type = 'username'
        db_usr = self.db.get_user_details_by_value(usr_input, input_type)
        if db_usr == None:
            # Account does not exist
            return {'code': 'error', 'msg': 'User does not exist.'}

        # if input is email we hash with that, otherwise we use db email  
        if db_usr.user_id == \
            hashify_user(db_usr.email, usr_pass, db_usr.creation_date):
            
            return {'code': 'success', 'msg': db_usr.user_id}
        
        return {'code': 'error', 'msg': 'One of the credentials is incorrect.'}

    def get_user_file_ids(self, user_id: str):
        return self.db.get_user_files(user_id)

    def get_user_filenames(self, user_id: str):
        filenames = []
        files_id = self.db.get_user_files(user_id)
        for fd in files_id:
            filename = self.db.get_file_name(fd)
            if filename != None:
                filenames.append(filename)
            
        return filenames
    
    def add_file_to_user(self, user_id: str, file_id: str):
        self.db.change_user_file_ids(user_id, file_id, 'add')
    
    def remove_file_from_user(self, user_id: str, file_id: str):
        self.db.change_user_file_ids(user_id, file_id, 'remove')

    def get_filename(self, file_id: str):
        return self.db.get_file_name(file_id)

if __name__ == '__main__':
    cs = CloudServer('127.0.0.1', 8081)

