import uuid

def get_rand_hash(length: int = 32) -> str:
    rnd_hash = uuid.uuid4().hex[:length]
    return rnd_hash

import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # генерирует уникальную "соль"
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
