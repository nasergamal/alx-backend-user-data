#!/usr/bin/env python3
""" Basic Auth
"""
from api.v1.auth.auth import Auth
import base64
from models.user import User
from typing import TypeVar


class BasicAuth(Auth):
    '''basic Authentication'''
    def extract_base64_authorization_header(self, authorization_header: str
                                            ) -> str:
        '''return Base64 of the Authorization header'''
        if (not authorization_header or type(authorization_header) != str or
                not authorization_header.startswith('Basic ')):
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str
                                           ) -> str:
        '''decode header'''
        try:
            return base64.b64decode(base64_authorization_header
                                    ).decode('utf-8')
        except (TypeError, base64.binascii.Error, UnicodeDecodeError):
            return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str
                                 ) -> (str, str):
        '''return user credentials'''
        if (not decoded_base64_authorization_header or
                type(decoded_base64_authorization_header) != str or
                ':' not in decoded_base64_authorization_header):
            return (None, None)
        sep = decoded_base64_authorization_header.find(':')
        cred = (decoded_base64_authorization_header[:sep],
                decoded_base64_authorization_header[sep + 1:])
        return cred

    def user_object_from_credentials(self, user_email: str, user_pwd: str
                                     ) -> TypeVar('User'):
        '''return user details from credentials'''
        if (not user_email or type(user_email) != str or
                not user_pwd or type(user_pwd) != str):
            return None
        user = User()
        res = user.search({'email': user_email})
        if not res:
            return None
        for result in res:
            if result.is_valid_password(user_pwd):
                return result
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        '''retreive user'''
        header = self.authorization_header(request)
        header = self.extract_base64_authorization_header(header)
        header = self.decode_base64_authorization_header(header)
        cred = self.extract_user_credentials(header)
        if cred[0]:
            return self.user_object_from_credentials(cred[0], cred[1])
        return None
