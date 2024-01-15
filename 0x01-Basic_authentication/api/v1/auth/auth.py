#!/usr/bin/env python3
'''Authentication Class'''
from flask import request
from typing import TypeVar, List
import re


class Auth:
    '''For handling of authentication'''
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        '''check of page require authentication'''
        if path and not path.endswith('/'):
            path = path + '/'
        if (not path or not excluded_paths):
            return True
        if path not in excluded_paths:
            for excluded in excluded_paths:
                if re.match(excluded, path):
                    return False
            return True
        return False

    def authorization_header(self, request=None) -> str:
        '''return auth from header'''
        if not request or request.headers.get('Authorization') is None:
            return None
        return request.headers.get('Authorization')

    def current_user(self, request=None) -> TypeVar('User'):
        '''empty function'''
        return None
