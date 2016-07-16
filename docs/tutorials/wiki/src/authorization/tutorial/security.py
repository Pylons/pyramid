import hashlib
import os
import binascii

SALT_LENGTH = 16


def hash_password_with_salt(password, salt=None):
    salt = salt or os.urandom(SALT_LENGTH)
    dk = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(dk + salt).decode('utf-8')

def check_password(password, salted_password):
    salt = binascii.unhexlify(salted_password[-2 * SALT_LENGTH:])
    return hash_password_with_salt(password, salt) == salted_password


USERS = {'editor': hash_password_with_salt('editor'),
         'viewer': hash_password_with_salt('viewer')}
GROUPS = {'editor': ['group:editors']}


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
