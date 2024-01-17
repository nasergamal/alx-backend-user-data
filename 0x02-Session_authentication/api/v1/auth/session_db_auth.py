#!/usr/bin/env python3
""" Session duration
"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from datetime import datetime, timedelta
from models.user_session import UserSession
from os import getenv


class SessionDBAuth(SessionExpAuth):
    '''Session database Authentication'''

    def create_session(self, user_id: str = None) -> str:
        '''create a new session id for user'''
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        new_session = UserSession(user_id=user_id, session_id=session_id)
        new_session.save()
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        '''returns a User ID based on a Session ID'''
        if session_id is None:
            return None
        UserSession.load_from_file()
        users = UserSession.search({'session_id': session_id})
        if not users:
            return None
        user = users[0]
        if self.session_duration <= 0:
            return user.user_id
        diff = timedelta(seconds=self.session_duration)
        if datetime.utcnow() - user.created_at < diff:
            return user.user_id
        return None

    def destroy_session(self, request=None):
        '''destroy UserSession '''
        if request is None:
            return False
        session_id = self.session_cookie(request)
        if session_id is None:
            return False
        users = UserSession.search({'session_id': session_id})
        if not users:
            return False
        users[0].remove()
        return True
