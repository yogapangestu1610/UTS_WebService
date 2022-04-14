# 6C/19090092/Hendra Estu Prasetyo
# 6C/19090126/Muhammad Fikri
# 6C/19090034/Muhammad Yoga Pangestu
# 6C/19090006/Hanifan Husein Isnanto

import os, random, string
from datetime import datetime
from flask import Flask
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "event.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class Users(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=True)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_creator = db.Column(db.String(50),nullable=False)
    event_name = db.Column(db.String(50),nullable=False)
    event_start_time = db.Column(db.Date, nullable=False)
    event_end_time = db.Column(db.Date, nullable=False)
    event_start_lat = db.Column(db.String(50),nullable=False)
    event_start_lng = db.Column(db.String(50),nullable=False)
    event_finish_lat = db.Column(db.String(50),nullable=False)
    event_finish_lng = db.Column(db.String(50),nullable=False)
    create_at = db.Column(db.Date, nullable=False, default=datetime.now)

class Logs(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    event_name = db.Column(db.String(50))
    log_lat = db.Column(db.String(50))
    log_lng = db.Column(db.String(50))
    create_at = db.Column(db.Date, default=datetime.now)

db.create_all()

#curl -i -X POST http://127.0.0.1:9200/api/v1/users/create -H 'Content-Type: application/json' -d '{"username":19090092, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/create -H 'Content-Type: application/json' -d '{"username":19090034, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/create -H 'Content-Type: application/json' -d '{"username":19090126, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/create -H 'Content-Type: application/json' -d '{"username":19090006, "password": 123}'

@app.route("/api/v1/users/create", methods=["POST"])
def create_user():
    username = request.json['username']
    password = request.json['password']

    newUsers = Users(username=username, password=password)

    db.session.add(newUsers)
    db.session.commit() 
    return jsonify({
        'msg': 'berhasil tambah user',
        'username': username,
        'password' : password,
        'status': 200 
        })

#curl -i -X POST http://127.0.0.1:9200/api/v1/users/login -H 'Content-Type: application/json' -d '{"username":19090092, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/login -H 'Content-Type: application/json' -d '{"username":19090034, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/login -H 'Content-Type: application/json' -d '{"username":19090006, "password": 123}'
#curl -i -X POST http://127.0.0.1:9200/api/v1/users/login -H 'Content-Type: application/json' -d '{"username":19090126, "password": 123}'

@app.route("/api/v1/users/login", methods=["POST"])
def login():
    username = request.json['username']
    password = request.json['password']

    user = Users.query.filter_by(username=username, password=password).first()

    if user:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        Users.query.filter_by(username=username, password=password).update({'token': token})
        db.session.commit()

        return jsonify({
        'msg': 'Login berhasil',
        'username': username,
        'token': token,
        'status': 200 
        })

    else:
        return jsonify({
        'msg': 'Login gagal',
        'status': 401,
        })

@app.route("/api/v1/events/create", methods=["POST"])
def create_event():

    token = request.json['token']

    token = Users.query.filter_by(token=token).first()
    if token:

        event_creator = token.username
        event_name = request.json['event_name']
        event_start_time = request.json['event_start_time']
        event_end_time = request.json['event_end_time']
        event_start_lat = request.json['event_start_lat']
        event_finish_lat = request.json['event_finish_lat']
        event_start_lng = request.json['event_start_lng']
        event_finish_lng = request.json['event_finish_lng']

        event_start_time = datetime.strptime(event_start_time, '%Y-%m-%d %H:%M:%S')
        event_end_time = datetime.strptime(event_end_time, '%Y-%m-%d %H:%M:%S')

        newEvent = Events(event_start_time=event_start_time, event_end_time=event_end_time, event_creator=event_creator, event_name=event_name, event_start_lat=event_start_lat, event_finish_lat=event_finish_lat, event_start_lng=event_start_lng, event_finish_lng=event_finish_lng)

        db.session.add(newEvent)
        db.session.commit() 

        return jsonify({
            'msg': 'berhasil tambah event'
            })

@app.route("/api/v1/events/log", methods=["POST"])
def event_log():
    token = request.json['token']

    token = Users.query.filter_by(token=token).first()

    if token:
        username = token.username
        event_name = request.json['event_name']
        log_lat = request.json['log_lat']
        log_lng = request.json['log_lng']
    
        newLog = Logs(username=username, event_name=event_name, log_lat=log_lat, log_lng=log_lng)

        db.session.add(newLog)
        db.session.commit() 

    return jsonify({
        'msg': 'Anda berhasil menambahkan posisi terbaru'
        })

@app.route("/api/v1/events/logs", methods=["GET"])
def event_logs():

    token = request.json['token']

    token = Users.query.filter_by(token=token).first()
    if token : 

        username = token.username
        event_name = request.json['event_name']
    
        logs_event = Logs.query.filter_by(event_name=event_name).all()

        logs_status = []

        for log in logs_event:
            dict_logs = {}
            dict_logs.update({"username": log.username, "event_name": log.event_name, "log_lat": log.log_lat, "log_lng": log.log_lng, "create_at": log.create_at })
            logs_status.append(dict_logs)
        
        return jsonify(logs_status)

if __name__ == '__main__':
    app.run(debug=True, port=3400)