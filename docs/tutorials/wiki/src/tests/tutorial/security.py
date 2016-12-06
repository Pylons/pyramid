import bcrypt


def hash_password(pw):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())

def check_password(expected_hash, pw):
    if expected_hash is not None:
        return bcrypt.checkpw(pw.encode('utf-8'), expected_hash)
    return False

USERS = {'editor': hash_password('editor'),
          'viewer': hash_password('viewer')}
GROUPS = {'editor':['group:editors']}

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
