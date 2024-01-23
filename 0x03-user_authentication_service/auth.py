#!/usr/bin/env python3
'''authentication methods'''
import bcrypt
from db import DB
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional
from user import User
from uuid import uuid4


def _hash_password(password: str) -> bytes:
    '''hash given password using bcrypt'''
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _generate_uuid() -> str:
    '''generate uuid'''
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        '''Auth init'''
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        '''create a new user instance in db'''
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists.")
        except NoResultFound:
            user = self._db.add_user(email, _hash_password(password))
            return user

    def valid_login(self, email: str, password: str) -> bool:
        '''validate credentials'''
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'),
                                  user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Optional[str]:
        '''create session id for user'''
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except InvalidRequestError:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        '''return the user corresponding to session id'''
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id):
        '''destroy user's session to logout'''
        try:
            self._db.find_user_by(id=user_id)
            self._db.update_user(user_id, session_id=None)
        except InvalidRequestError:
            pass

    def get_reset_password_token(self, email: str) -> str:
        '''get user password reset token'''
        try:
            user = self._db.find_user_by(email=email)
            reset_token = _generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str):
        '''reset password'''
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            self._db.update_user(user.id,
                                 hashed_password=_hash_password(password),
                                 reset_token=None)
        except NoResultFound:
            raise ValueError
