#!/usr/bin/env python3
""" Session duration
"""
from api.v1.auth.session_auth import SessionAuth
from datetime import datetime, timedelta
from models.user import User
from os import getenv


class SessionExpAuth(SessionAuth):
    '''Session Authentication'''

    def __init__(self):
        '''set duration'''
        try:
            duration = int(getenv('SESSION_DURATION'))
        except TypeError:
            duration = 0
        self.session_duration = duration

    def create_session(self, user_id: str = None) -> str:
        '''create a new session id for user'''
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        self.user_id_by_session_id[session_id] = {'user_id': user_id,
                                                  'created_at': datetime.now()}
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        '''returns a User ID based on a Session ID'''
        if session_id is None or type(session_id) != str:
            return None
        session = self.user_id_by_session_id.get(session_id)
        if not session:
            return None
        if self.session_duration <= 0:
            return session.get('user_id')
        if not session.get('created_at'):
            return None
        diff = timedelta(seconds=self.session_duration)
        if datetime.now() - session.get('created_at') < diff:
            return session.get('user_id')
        return None
