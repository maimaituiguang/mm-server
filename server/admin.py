# -*- coding: utf-8 -*-

from flask import request, url_for, render_template, Blueprint, make_response, session, redirect, Response
import adminQuery
import time, json

admin_api = Blueprint('admin_api', __name__)

@admin_api.before_request
def before_request():
    if request.path == '/login':
        return None

    if 'username' not in session:
        return redirect(url_for('admin_api.login'))

@admin_api.route('/login', methods=['POST', 'GET'])
def login():
    ck = request.cookies.get('username')
    if ck:
        session['username'] = ck
        return redirect(url_for('admin_api.home'))

    if request.method == 'POST':
        data = json.loads(request.get_data())
        username = data['phone']
        password = data['password']
        if adminQuery.verify_user(username, password):
            session['username'] = username
            res = make_response(json.dumps({'success': True}))
            res.set_cookie('username', username, expires=time.time() + 6 * 60 * 24 * 30)
            return res
        else:
            return json.dumps({'success': False, 'info': '账号或密码错误'})

    return render_template('login.html')


@admin_api.route('/home', methods=['GET'])
def home():
    return render_template('home.html')



def __response(json):
    return Response(json, mimetype='application/json')