from datetime import datetime, timedelta
import os
import sqlite3
import threading
from time import sleep, time
from DBObjects import DBFile, DBUser

class DBCommands:
    def __init__(self, db_file_path: str):
        self.db_file_path = db_file_path
        self.db_con = sqlite3.connect(db_file_path, check_same_thread=False)
        self.cur = self.db_con.cursor() # Will be used to operate in db
        self.lock = threading.Lock()
    
    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS files
        (file_id text primary key, in_dir integer, name text, content blob, added_date text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
        (user_id text primary key, username text, email text, creation_date text, files text, trusted_agents text)''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS dirs
        (dir_id text primary key, name text, files text)''')
        
        self.db_con.commit()
        
    # Files
    
    def add_file(self, file: DBFile):
        try:
            self.lock.acquire(True)
            self.cur.execute(f'''INSERT INTO files(file_id, in_dir, name, content, added_date)
            values (?, ?, ?, ?, ?)''',
            (file.file_id, '1' if file.in_dir else '0', file.name, file.content, str(file.added_date.strftime("%d/%m/%Y, %H:%M:%S"))))
            self.db_con.commit()
        finally:
            self.lock.release()

    def remove_file_by_name(self, filename: str):
        self.cur.execute(f'''DELETE FROM files WHERE name=:filename''', {'filename': filename})
        self.db_con.commit()

    def remove_file_by_id(self, file_id: str):
        self.cur.execute(f'''DELETE FROM files WHERE file_id=:file_id''', {'file_id': file_id})
        self.db_con.commit()
    
    def get_file_name(self, file_id: str):
        self.cur.execute(f'''SELECT name FROM files WHERE file_id=:file_id''', {'file_id': file_id})
        ans = self.cur.fetchall()
        if len(ans) == 0:
            return None
        
        name = ans[0][0] # If more than a file popps up, that is a problem
        return name # Bytes of the file

    def get_file_content(self, file_id: str):
        self.cur.execute(f'''SELECT content FROM files WHERE file_id=:file_id''', {'file_id': file_id})
        ans = self.cur.fetchall()
        if len(ans) == 0:
            return None
        content = ans[0][0] # If more than a file popps up, that is a problem
        return content # Bytes of the file
        
    # Users

    def add_user(self, usr: DBUser):
        self.cur.execute(f'''INSERT INTO users(user_id, username, email, creation_date, files, trusted_agents)
        values (?, ?, ?, ?, ?, ?)''',
        (usr.user_id,usr.username, usr.email, str(usr.creation_date.strftime("%d/%m/%Y, %H:%M:%S")), ','.join(usr.files), ''))
        self.db_con.commit()
    
    def remove_user_by_username(self, username: str):
        self.cur.execute(f'''DELETE FROM users WHERE username=:username''', {'username': username})
        self.db_con.commit()

    def remove_user_by_id(self, id: str):
        self.cur.execute(f'''DELETE FROM users WHERE user_id=:id''', {'id': id})
        self.db_con.commit()

    def get_user_details_by_value(self, value: str, input_type: str):
        if input_type not in ['user_id', 'username', 'email']:
            # You can find user only with those value types
            return None
        
        # command based on given type
        fetch_command = f'''SELECT * FROM users WHERE {input_type}=:{input_type}'''
        self.cur.execute(fetch_command, {input_type: value})
        ans = self.cur.fetchall()
        if len(ans) == 0:
            return None

        user = ans[0] # Should be only one user
        userid, username, email, creation_date, files, trusted_agents = user # Splitting the tuple
        return DBUser(userid, username, email, datetime.strptime(creation_date, "%d/%m/%Y, %H:%M:%S"), files.split(','), trusted_agents.split(','))


    def check_email_existance(self, email: str):
        self.cur.execute(f'''SELECT * FROM users WHERE email=:email''', {'email': email})
        ans = self.cur.fetchall()
        if len(ans) == 0: # empty list = no accounts
            return False
        return True
    
    def check_username_existance(self, username: str):
        self.cur.execute(f'''SELECT * FROM users WHERE username=:username''', {'username': username})
        ans = self.cur.fetchall()
        if len(ans) == 0: # empty list = no accounts
            return False
        return True
    
    def get_user_files(self, user_id: str): # file_ids
        try:
            self.lock.acquire(True)
            self.cur.execute(f'''SELECT files FROM users WHERE user_id=:user_id''', {'user_id': user_id})
            ans = self.cur.fetchall()
            if len(ans) == 0: # empty list = no accounts
                return []
            
            if ans[0][0] == '':
                return []
            else:
                return ans[0][0].split(',')
        finally:
            self.lock.release()
            
    def change_user_file_ids(self, user_id: str, file_id: str, change_type: str):
        if change_type not in ['remove', 'add']:
            return None

        try:
            self.lock.acquire(True)
            self.cur.execute(f'''SELECT files FROM users WHERE user_id=:user_id''', {'user_id': user_id})
            ans = self.cur.fetchall()

            if len(ans) > 0 and ans[0][0] == '':
                self.cur.execute(f'''UPDATE users SET files=:file_id WHERE user_id=:user_id''', {'file_id': file_id, 'user_id': user_id})
            else:
                files = ans[0][0].split(',')
                
                
                if change_type == 'add':
                    files.append(file_id)
                else:
                    files.remove(file_id)
                new_files = ','.join(files)

                
                self.cur.execute(f'''UPDATE users SET files=:new_files WHERE user_id=:user_id''',
                {'new_files': new_files, 'user_id': user_id})

            self.db_con.commit()   
        finally:
            self.lock.release()

    # user-agents

    def change_user_agents_status(self, user_id: str, agent: str, change_type: str):
        # Agent should be some kind a hash (token)
        
        transformed_agent = f'{agent}|{datetime.timestamp(datetime.now())}' # Agents: asdc1sad5f4asd23|datetime
        if change_type not in ['remove', 'add']:
            return None

        try:
            self.lock.acquire(True)
            self.cur.execute(f'''SELECT trusted_agents FROM users WHERE user_id=:user_id''', {'user_id': user_id})
            ans = self.cur.fetchall()

            if len(ans) > 0 and ans[0][0] == '':
                self.cur.execute(f'''UPDATE users SET trusted_agents=:agent WHERE user_id=:user_id''', {'agent': transformed_agent, 'user_id': user_id})
            else:
                trusted_agents = ans[0][0].split(',')
                
                
                if change_type == 'add':
                    trusted_agents.append(transformed_agent)
                else: # Deleting 
                    for ag in trusted_agents:
                        if agent in ag: # Because of dates we need to search
                            trusted_agents.remove(ag)
                new_agents = ','.join(trusted_agents)

                
                self.cur.execute(f'''UPDATE users SET trusted_agents=:new_agents WHERE user_id=:user_id''',
                {'new_agents': new_agents, 'user_id': user_id})

            self.db_con.commit()   
        finally:
            self.lock.release()

    def filter_user_agents(self, days_interval: int):
        print(f'Deleting trusted agents from all accounts that last logged {days_interval} days ago.')
        try:
            self.lock.acquire(True)
            self.cur.execute(f'''SELECT trusted_agents, user_id FROM users''')
            ans = self.cur.fetchall()

            for user_trusted_agents, user_id in ans:
                delete_agents = []
                
                if user_trusted_agents == '':
                    print('No trusted agents for ->', user_id)
                    continue

                for agent in user_trusted_agents.split(','):
                    agent_hash, timestamp = agent.split('|')
                    time_gone = (datetime.now() - datetime.fromtimestamp(float(timestamp)))
                    
                    if time_gone.days > days_interval:
                        delete_agents.append(agent)
                
                new_agents_list = user_trusted_agents.split(',')
                # Now we delete outdated agents
                for ag in delete_agents:
                    new_agents_list.remove(ag)

                        # On success connection -> Add a user-agent
                        # On redirection to auth code -> Check if user-agent is trusted
                
                # Finally, update db
                self.cur.execute(f'''UPDATE users SET trusted_agents=:agents WHERE user_id=:user_id''', {'agents': ','.join(new_agents_list), 'user_id': user_id})
                
            self.db_con.commit()
        finally:
            self.lock.release()

    # Runs on deconstruction of object
    def __del__(self):
        print('Closing db connection')
        self.cur.close()

    def __repr__(self) -> str:
        return f'db api for -> {self.db_file_path}'
        

if __name__ == "__main__":
    # Testing register of 2 accounts and adding file
    os.remove('./database.db')

    db = DBCommands('./database.db')
    db.create_tables()
    db.add_user(DBUser('u1', 'ilan', 'something@gm.com', datetime.now(), ''))
    for i in range(4):
        db.change_user_file_ids('u1', f'f{i}', 'add')
    
    db.add_user(DBUser('u2', 'ron', 'something2@gm.com', datetime.now(), ''))
    for i in range(4):
        db.change_user_file_ids('u2', f'ff{i}', 'add')

    # Testing trusted agents
    db.change_user_agents_status('u1', 'aaa', 'add')
    sleep(4)
    db.change_user_agents_status('u1', 'bbbbbb', 'add')
    sleep(4)
    db.change_user_agents_status('u2', 'ccccc', 'add')
    print('check')
    db.filter_user_agents(6)

    sleep(2)
    db.filter_user_agents(1)  

    print('check')
    sleep(5)
    
    db.change_user_agents_status('u1', 'aaa', 'add')
    db.change_user_agents_status('u1', 'bbbbbb', 'add')
    db.change_user_agents_status('u2', 'ccccc', 'add') 


    
    