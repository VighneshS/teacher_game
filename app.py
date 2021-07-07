import datetime
import os
from dataclasses import dataclass

import sqlalchemy
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

server = os.environ['UD_HOST_NAME']
database = os.environ['UD_DB_NAME']
username = os.environ['UD_DB_USERNAME']
password = os.environ['UD_DB_PASSWORD']

secretKey = os.environ['SECRET_KEY']

app = Flask(__name__)
app.secret_key = secretKey

# enable debugging mode
app.config["DEBUG"] = True

connection_string = "mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4".format(username, password, server, database)

engine = create_engine(connection_string)

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)


@dataclass
class Game(db.Model):
    __tablename__ = 'game'
    id: int
    red_name: str
    green_name: str
    red: int
    green: int
    turn: str
    start_time: datetime

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    red_name = db.Column(sqlalchemy.VARCHAR(200))
    green_name = db.Column(sqlalchemy.VARCHAR(200))
    red = db.Column(sqlalchemy.Integer())
    green = db.Column(sqlalchemy.Integer())
    turn = db.Column(sqlalchemy.CHAR(1))
    start_time = db.Column(sqlalchemy.TIMESTAMP)

    @property
    def serializable(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'red_name': self.red_name,
            'green_name': self.green_name,
            'red': self.red,
            'green': self.green,
            'turn': self.turn,
            'start_time': self.start_time
        }


@app.route('/', methods=['GET'])
def home():
    game = Game.query.all()
    print(game)
    if not game or not game[0].red_name:
        if len(game) <= 0:
            game = Game(red=5, green=5)
            db.session.add(game)
            db.session.commit()
        return render_template('index.html')
    else:
        return render_template('quiz.html')


def update_name(name):
    game = Game.query.one()
    game.red_name = name
    game.start_time = datetime.datetime.now()
    db.session.add(game)
    db.session.commit()
    return game


def decrement_rock():
    game = Game.query.one()
    game.red -= 1
    db.session.add(game)
    db.session.commit()
    return game


def delete_all_data():
    Game.query.delete()
    db.session.commit()
    return {"status": "Delete success"}


@app.route('/name', methods=['POST'])
def save_name():
    print(request.get_json()['name'])
    return jsonify(update_name(request.get_json()['name']))


@app.route('/rock', methods=['POST'])
def save_question():
    return jsonify(decrement_rock())


@app.route('/end', methods=['POST'])
def end_quiz():
    return jsonify(delete_all_data())


@app.route('/status')
def hello_world():
    return "Hello World"


@app.route('/stream')
def game_stream():
    data = {}
    games = Game.query.all()
    if games:
        data = games[0]
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
