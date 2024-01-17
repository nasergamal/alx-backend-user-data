#!/usr/bin/env python3
""" Module of Users views
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
from os import getenv


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def session_handler() -> str:
    """ POST /api/v1/auth_session/login
    """
    email = request.form.get('email')
    pwd = request.form.get('password')
    if not email:
        return jsonify({"error": "email missing"}), 400
    if not pwd:
        return jsonify({"error": "password missing"}), 400
    results = User.search({'email': email})
    if not results:
        return jsonify({"error": "no user found for this email"}), 404
    user = results[0]
    if not user.is_valid_password(pwd):
        return jsonify({"error": "wrong password"}), 401
    from api.v1.app import auth
    s = auth.create_session(user.id)
    output = jsonify(user.to_json(), 200)
    output.set_cookie(getenv('SESSION_NAME', ' _my_session_id'), s)
    return output


@app_views.route('auth_session/logout',
                 methods=['DELETE'], strict_slashes=False)
def session_destroyer():
    """ DELETE /api/v1/auth_session/logout
    """
    from api.v1.app import auth
    if auth.destroy_session(request) is False:
        abort(404)
    return {}, 200
