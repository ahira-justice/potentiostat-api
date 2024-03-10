import hashlib
import os
import random

from typing import Tuple


def generate_hash_and_salt(password: str) -> Tuple[bytes, bytes]:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000,
        dklen=128
    )

    return key, salt


def generate_code(length: int, key_space: str) -> str:
    return ''.join((random.choice(key_space) for x in range(length)))
