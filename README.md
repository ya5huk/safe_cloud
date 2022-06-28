# SafeCloud ☁️
An online files-storage app designed to be fast & easy to use. Built for people who don't want to mess with too much buttons 
and use apps like Google Drive / iCloud purely for functionality. 
- [Hebrew Project Book](https://github.com/ya5huk/safe_cloud/blob/master/Hebrew%20Explanation/Hebrew%20Project%20Book.pdf)
- [Youtube demo](https://youtu.be/M82mEZAnpvk)

## Features

🚀 Delete & Download with one-click

🚀 Add single / multiple files with simple drag & drop

🚀 Two-step email authentication

🚀 Client side file encryption

## Run the app
First clone the git repo:
`git clone https://github.com/ya5huk/safe_cloud`

Download the relevant libraries described in `requirements.txt` using `pip`:
`pip install -r requirements.txt`

Initialize relevant environment variables in a file `.env` (Add the file yourself). The file must include:
- `EMAIL_USERNAME`, the 2step auth sender username
- `EMAIL_PASSWORD`, the 2step auth sender password (Note that this needs to be an [app password](https://support.google.com/accounts/answer/185833?hl=en))
- `IS_IT_A_REAL_EMAIL_API_KEY`, an api key for https://isitarealemail.com/. NOTE that the api does not work consistantly and used more for theoretic-use (Good email validators cost money)

Finally, run the app using
`py app.py` or `python app.py`
and enter `http://127.0.0.1:5000/`


## Main Technologies
As mentioned in the book, here are the main technologies:
- [Flask](https://flask.palletsprojects.com/en/2.1.x/), a python framework to run web apps written in Python
- [Flask-Session](https://flask-session.readthedocs.io/en/latest/), a flask add-on that enables option for sessions to be saved in other places than client-side
- [Smtplib](https://docs.python.org/3/library/smtplib.html), A library for SSL-Mail connection. Used for the 2-step authentication
- [Email checker](https://isitarealemail.com/), Used to determine whether an email is valid (prevent useless sending)
- [CryptoJS](https://cryptojs.gitbook.io/docs/), for AES encryption with javascript (client-side)
- [jquery](https://jquery.com/), for dynamic website changes (f.e. adding a file & updating file list on the page)  
- [Bootstrap](https://getbootstrap.com/), to speed up and ease the frontend developing

