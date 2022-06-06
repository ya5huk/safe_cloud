from datetime import datetime
from DBCommands import DBCommands
from DBObjects import DBFile
import uuid
import socket
import threading
import os
import base64

class Codes:
    ADD_FILE = '101'
    GET_FILE_CONTENT = '102'
    DELETE_FILE = '103'

MAX_FILENAME_SIZE = 50

class CloudServer:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = self.create_sock()
        self.clients = []

        self.server_listen()

    def server_listen(self):
        while True:
            try:
                conn, addr = self.sock.accept()
            except KeyboardInterrupt as e:
                print('Server closed.')
                break
                
            print(f'{addr} has connected')
            client_thread = threading.Thread(target=self.client_convo, args=(conn,))
            client_thread.start()
            
            # Store all connected clients info
            self.clients.append({
                "address": addr,
                "socket": conn,
                "thread": client_thread
            })
            
    def client_convo(self, conn: socket.socket):
        # Open a db instance for that thread
        db = DBCommands('D:\\USER\\Desktop\\safe_cloud\\user.db')
        db.create_tables() # For new accounts
        print(db)

        # A thread to run for each client
        try:
            while True:
                op_code = conn.recv(3)
                if not op_code:
                    break
                match op_code.decode():
                    case Codes.ADD_FILE:
                        self.add_file(conn, db)
                    case Codes.GET_FILE_CONTENT:
                        self.send_file_content(conn, db)
                    case Codes.DELETE_FILE:
                        self.delete_file(conn, db)
                    case _:
                        pass
        except Exception as e:
            print(f'Probably a connection loss: {e}')
            db.close()

    def create_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen()
        return sock

    @staticmethod
    def add_file(conn: socket.socket, db: DBCommands):
        in_dir = True if conn.recv(1).decode() == '1' else False
        
        namelen = int(conn.recv(8).decode())
        filename = conn.recv(namelen).decode()
        
        content_len = int(conn.recv(32).decode())
        recieved_bytes = 0
        content = bytes()
        while recieved_bytes < content_len:
            content += conn.recv(1024)
            recieved_bytes += 1024
        
        file_id = str(uuid.uuid1()) # By timestamp
        creation_time = datetime.now()
        
        file = DBFile(file_id, in_dir, filename, content, creation_time)
        
        print('Adding file: ', file)
        db.add_file(file)

        # After file is added, send back the icon to the client
        # so website will show file's added icon
        
        ext = filename.split('.')[-1]
        default_path = 'D:\\USER\\Desktop\\safe_cloud\\images\\extension_icons\\_blank.png'
        desired_path = f'D:\\USER\\Desktop\\safe_cloud\\images\\extension_icons\\{ext}.png'
        
        if os.path.exists(desired_path):
            final_path = desired_path
        else:
            final_path = default_path
        
        with open(final_path, 'rb') as f:
            icon_content = f.read()
        
        
        conn.send(zero_message(len(icon_content), 32).encode())
        conn.send(icon_content)
    
    @staticmethod
    def send_file_content(conn: socket.socket, db: DBCommands):
        filename = conn.recv(MAX_FILENAME_SIZE).decode()
        content = db.get_file_content(filename)
        conn.send(zero_message(len(content), 32).encode())
        conn.send(content)

    @staticmethod
    def delete_file(conn: socket.socket, db: DBCommands):
        filename = conn.recv(MAX_FILENAME_SIZE).decode()
        db.remove_file(filename)

class CloudClient:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def send_file(self, in_dir: bool, filename: str, content: bytes):
        # PROTOCOL
        # Meaning CODE-INDIR-FILENAMELENGTH-NAME-FILE
        # Sizes -3-1-8-dynamic-32-dynamic
        self.sock.send(Codes.ADD_FILE.encode())
        self.sock.send('1'.encode() if in_dir else '0'.encode())
        self.sock.send(zero_message(len(filename), 8).encode())
        self.sock.send(filename.encode())
        self.sock.send(zero_message(len(content), 32).encode()) # 2^32 bytes = about 4 GB's max
        self.sock.send(content)

        file_icon_size = int(self.sock.recv(32).decode())
        file_icon_data = bytes()
        bytes_read = 0
        
        while bytes_read < file_icon_size:
            file_icon_data += self.sock.recv(1024)
            bytes_read += 1024
        
        # turn file_icon_data into base64 because web only knows how to deal
        # with base64
        return base64.b64encode(file_icon_data)
    
    def get_file(self, filename: str):
        self.sock.send(Codes.GET_FILE_CONTENT.encode())
        self.sock.send(filename.encode())

        content_size = int(self.sock.recv(32).decode())
        content = bytes()
        bytes_read = 0
        while bytes_read < content_size:
            content += self.sock.recv(1024)
            bytes_read += 1024
        
        return base64.b64encode(content) # b64 is more web-friendly
    
    def delete_file(self, filename: str):
        self.sock.send(Codes.DELETE_FILE.encode())
        self.sock.send(filename.encode())
    

def zero_message(num: int, digits_num: int):
    # Adds zeros before the number if possible TO MATCH digits_num DIGITS
    return (digits_num-len(str(num)))*'0' + str(num)

if __name__ == '__main__':
    cs = CloudServer('127.0.0.1', 8081)

