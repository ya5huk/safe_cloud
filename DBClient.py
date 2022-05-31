import firebase_admin
from firebase_admin import credentials, firestore
from DBObjects import DBFile

class DBClient:
    def __init__(self, firestore_json_path):
        self.cred = credentials.Certificate(firestore_json_path)
        firebase_admin.initialize_app(self.cred)
        self.app_cli = firestore.client()

    def add_file(self, file: DBFile):
        self.app_cli.collection('files').document().set(file.to_dict())