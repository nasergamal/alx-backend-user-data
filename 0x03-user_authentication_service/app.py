#!/usr/bin/env python3
'''flask app'''
from flask import Flask, jsonify, request, abort, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route('/')
def home() -> str:
    '''home page'''
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'])
def users() -> str:
    '''User registration'''
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'])
def login() -> str:
    '''login'''
    email = request.form.get('email')
    password = request.form.get('password')
    if AUTH.valid_login(email, password):
        id = AUTH.create_session(email)
        res = jsonify({"email": email, "message": "logged in"})
        res.set_cookie('session_id', id)
        return res
    else:
        abort(401)


@app.route('/sessions', methods=['DELETE'])
def logout():
    '''user logout'''
    id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET'])
def profile():
    '''user profile'''
    id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(id)
    if user:
        return jsonify({'email': user.email})
    abort(403)


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token():
    '''get reset token'''
    email = request.form.get('email')
    try:
        token = AUTH.get_reset_password_token(email)
        return jsonify({'email': email, 'reset_token': token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'])
def update_password():
    '''password change'''
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    pwd = request.form.get('new_password')
    try:
        AUTH.update_password(reset_token, pwd)
        return jsonify({'email': email, "message": "Password updated"})
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
