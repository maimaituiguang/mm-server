# -*- coding: UTF-8 -*-

from flask import Flask, Response, request, jsonify
import query
import json
from admin import admin_api

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?R/LJDHCS/,/s'
app.register_blueprint(admin_api)


@app.route('/account')
def account():
    re = query.account(request)
    if not isinstance(re, dict):
        return __response(json.dumps({'success': False}))

    return __response(json.dumps({'success': True, 'data': re}))


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        re = query.register(request)
        if isinstance(re, dict):
            return __response(json.dumps({'success': True, 'data': re}))

    return __response(json.dumps({'success': False}))


@app.route('/client-login', methods=['POST'])
def client_login():
    if request.method == 'POST':
        re = query.client_login(request)
        if isinstance(re, dict):
            return __response(json.dumps({'success': True, 'data': re}))
        else:
            return __response(json.dumps({'success': False, 'data': re}))

    return __response(json.dumps({'success': False}))


@app.route('/apps/<int:offset>')
def apps(offset):
    return __response(query.apps(offset))


@app.route('/task')
def task():
    return __response(query.task(request))


@app.route('/submit-task', methods=['POST'])
def submit_task():
    if request.method == 'POST':
        return __response(json.dumps({'success': query.submit_task(request)}))
    return __response(json.dumps({'success': False}))


@app.route('/wallet', methods=['GET'])
def wallet():
    re = query.wallet(request)
    if isinstance(re, dict):
        return __response(json.dumps({'success': True, 'data': re}))

    return __response(json.dumps({'success': False}))


@app.route('/all-task/<int:offset>')
def all_task(offset):
    return __response(query.all_task(offset))


@app.route('/take', methods=['POST'])
def take():
    if request.method == 'POST':
        return __response(json.dumps({'success': query.take(request)}))
    return __response(json.dumps({'success': False}))


@app.route('/reward-record')
def record():
    return __response(query.record(request))


@app.route('/view-task/<int:status>')
def view_task(status):
    return __response(query.view_task(request, status))


@app.route('/members')
def members():
    return __response(query.members())


@app.route('/update-account', methods=['POST'])
def update_account():
    if request.method == 'POST':
        return __response(json.dumps({'success': query.update_account(request)}))
    return __response(json.dumps({'success': False}))


@app.route('/message')
def message():
    return __response(json.dumps({'text': ''}))


@app.route('/banner')
def banner():
    data = ['https://maimaituiguang.github.io/mm-web/images/banner8.png', 
    'https://maimaituiguang.github.io/mm-web/images/banner3.png',
    'https://maimaituiguang.github.io/mm-web/images/banner1.png']
    return __response(json.dumps({'data': data}))


@app.route('/customer')
def customer():
    data = {'QQ': '2582985333\n1467131226'}
    return __response(json.dumps(data))


@app.route('/sub-account-list')
def sub_account_list():
    return __response(json.dumps(query.sub_account_list(request)))


@app.route('/add-account')
def add_account():
    return __response(json.dumps(query.add_account(request)))


@app.route('/append_sub_password', methods=['POST'])
def append_sub_password():
    return jsonify(query.append_sub_password(request))

def __response(json):
    return Response(json, mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

