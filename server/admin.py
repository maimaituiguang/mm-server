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

# @admin_api.route('/')
# @admin_api.route('/index')
# def index():
#     return render_template('board.html')

@admin_api.route('/')
@admin_api.route('/home')
def home():
    return render_template('home.html')

@admin_api.route('/check-task')
def check_task():
    return render_template('task.html')

@admin_api.route('/check-reward')
def check_reward():
    return render_template('reward.html')

@admin_api.route('/wallet-list')
def wallet_list():
    return render_template('takes.html')









@admin_api.route('/search-user/<string:phone>')
def search(phone):
    return __response(adminQuery.search(phone))

@admin_api.route('/update-role/<int:role>/<string:phone>')
def update_role(role=None, phone=None):
    return __response(adminQuery.update_role(role, phone))

@admin_api.route('/update-status/<int:task_status>/<string:phone>')
def update_status(task_status=None, phone=None):
    return __response(adminQuery.update_status(task_status, phone))

@admin_api.route('/finished-task/<int:offset>')
def finished_task(offset):
    return __response(adminQuery.finished_task(offset))

@admin_api.route('/task-pass', methods=['POST'])
def task_pass():
    return __response(adminQuery.task_pass(request))

@admin_api.route('/all-take/<int:offset>')
def all_take(offset):
    return __response(adminQuery.all_take(offset))

@admin_api.route('/take-finished/<string:_id>/<int:status>')
def take_finished(_id, status):
    return __response(adminQuery.take_finished(_id, status))


@admin_api.route('/take-detail')
def take_detail():
    return __response(adminQuery.wallet_list())


def __response(json):
    return Response(json, mimetype='application/json')


