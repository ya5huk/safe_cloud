import random
import requests
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from decouple import config  # For enviorment variables

class TwoStepAuth:
    def __init__(self, sender_email: str):
        # Personal details
        self.sender_email = sender_email
        self.smtp_server = 'smtp.gmail.com'
        
        # Create .env for these
        self.username = config('EMAIL_USERNAME')
        self.password = config('EMAIL_PASSWORD')
        self.api_email_check_key = config('IS_IT_A_REAL_EMAIL_API_KEY')

        hidden_pass = self.password[:5] + '*'*(len(self.password) - 5) # So users can't see full pass
        print(f'Trying to log in with {self.username}, {hidden_pass}... ', end='')
        
        self.conn = SMTP_SSL(self.smtp_server, 465)
        self.conn.set_debuglevel(False)
        self.conn.login(self.username, self.password)
        print('Logged in!')

    @staticmethod
    def check_if_email_exists(email_address: str, api_key: str):
        url = 'https://isitarealemail.com/api/email/validate' # A blessing for developers
        res = requests.get(url, params={'email': email_address}, headers={'Authorization': f'Bearer {api_key}'})
        status = res.json()['status']
        
		# NOTE api is not consistant for reasons that are not under my controls. 
		# For producion use, I would use another email-validator api
        if status == 'valid':
            return True
        return False
    
            

    def send_code(self, code: str, dest_email: str):
        # Beautify
        text_subtype = 'html'
        content = f"""\
        <p>Thanks for logging in.</p>
        <p>Code: <b>{code}</b></p>
        """
        subject = 'SafeCloud code confiramtion'
        try:
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = 'SafeCloud'
            self.conn.sendmail(self.sender_email, dest_email, msg.as_string())

        except Exception as e:
            print(f'Message failed: {e}')

    def __del__(self):
        print('Closing smtp connection')
        self.conn.close()

    @staticmethod
    def generate_code(len: int):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        letters_big = letters.upper()
        digits = '0123456789'
        final_str = ''
        for i in range(len):
            element = random.choice([letters, letters_big, digits])
            final_str += random.choice(element)
        return final_str
    