from email.policy import default
import socket
import threading

# OPERATION CODES
ADD_FILE = 101


class CloudServer:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = self.create_sock(ip, port)
        self.clients = []

    def server_listen(self):
        while True:
            conn, addr = self.sock.accept()
            print(f'{addr} has connected')
            client_thread = threading.Thread(target=self.client_convo, args=conn,)
            client_thread.start()
            
            # Store all connected clients info
            self.clients.append({
                "address": addr,
                "socket": conn,
                "thread": client_thread
            })
            
    def client_convo(conn: socket.socket):
        # A thread to run for each client
        while True:
            op_code = conn.recv(8)
            if not op_code:
                break
            match int(op_code.decode()):
                case ADD_FILE:
                    pass
                case _:
                    pass

    def create_sock(ip: str, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, port))
        sock.listen()
        return sock

class CloudClient:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def send_file(self, in_dir: bool, filepath: str, content: bytes):
        self.sock.send(DB_OPERATION)
    
    