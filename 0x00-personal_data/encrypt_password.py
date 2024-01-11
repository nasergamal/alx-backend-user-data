#!/usr/bin/env python3
'''ecryptions for logging'''
import bcrypt


def hash_password(password: str) -> bytes:
    '''password hashing'''
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    '''validate hashed password'''
    return bcrypt.checkpw(password.encode(), hashed_password)
