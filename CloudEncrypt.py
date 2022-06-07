import hashlib
from datetime import datetime

# Fun fact I was stuck here because I hash wasn't const
# I had no idea why cuz I entered the same parameters
# I digged and digged and finally 
# print(creation_date.timestamp)
# this line returned different answers overtime 
# And it is because it printed a loc in memory when all I needed to do:
# is creation_date.timestamp() -> (It is a func)
# later I figured out that timestamp is more accurate when datetime.now()
# than the timestamp I am saving in the database :/
# So yea - a quick story


def hashify_user(email: str, password: str, creation_date: datetime):
    # Some dynamic salting for md5 hash

    creation_time_mixed = str(creation_date.timestamp())[::-2]
    salt = hashlib.md5(email.encode()).digest()[::2] + \
    hashlib.md5(creation_time_mixed.encode()).digest()[::3]    
    encstr = hashlib.md5(password.encode() + salt).hexdigest()
    return encstr
