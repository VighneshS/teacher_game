import atexit
import datetime
import json
import os
from dataclasses import dataclass

import redis
import sqlalchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, orm
from sqlalchemy.orm import relationship

server = os.environ['UD_HOST_NAME']
database = os.environ['UD_DB_NAME']
username = os.environ['UD_DB_USERNAME']
password = os.environ['UD_DB_PASSWORD']

secretKey = os.environ['SECRET_KEY']

redisHost = os.environ['REDIS_HOST']
redisPassword = os.environ['REDIS_PASSWORD']

GAME_CHANNEL = 'game_teacher'

r = redis.StrictRedis(host=redisHost, port=6379, password=redisPassword, db=0, charset='utf-8', decode_responses=True)

app = Flask(__name__)
app.secret_key = secretKey

# enable debugging mode
app.config["DEBUG"] = True

connection_string = "mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4".format(username, password, server, database)

engine = create_engine(connection_string)

app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)


@dataclass
class Teacher(db.Model):
    __tablename__ = 'teacher'
    id: int
    name: str

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(sqlalchemy.VARCHAR(200))
    game = relationship("Game")

    @property
    def serializable(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name
        }


@dataclass
class Student(db.Model):
    __tablename__ = 'student'
    id: int
    name: str

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(sqlalchemy.VARCHAR(200))
    game = relationship("Game")

    @property
    def serializable(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name
        }


@dataclass
class Game(db.Model):
    __tablename__ = 'game'
    id: int
    teacher_id: int
    student_id: int
    admin_name: str
    created_on: datetime

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    teacher_id = db.Column(sqlalchemy.Integer(), ForeignKey('teacher.id'))
    teacher = relationship("Teacher", back_populates="game", lazy='joined')
    student_id = db.Column(sqlalchemy.Integer(), ForeignKey('student.id'))
    student = relationship("Student", back_populates="game", lazy='joined')
    questions = relationship("QuestionAnswer", backref="game", lazy='joined')
    admin_name = db.Column(sqlalchemy.VARCHAR(200))
    created_on = db.Column(sqlalchemy.TIMESTAMP)

    @property
    def serializable(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'teacher': {} if not self.teacher else self.teacher.serializable,
            'student': {} if not self.student else self.student.serializable,
            'questions': self.questions,
            'admin_name': self.admin_name,
            'created_on': self.created_on.isoformat() + 'Z'
        }


@dataclass
class QuestionAnswer(db.Model):
    __tablename__ = 'question_answers'
    id: int
    game_id: int
    question: str
    answer: str
    score: int

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    game_id = db.Column(sqlalchemy.Integer(), ForeignKey('game.id'))
    question = db.Column(sqlalchemy.VARCHAR(200))
    answer = db.Column(sqlalchemy.VARCHAR(200))
    score = db.Column(sqlalchemy.Integer())

    @property
    def serializable(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'score': self.score,
        }


@app.route('/', methods=['GET'])
def home():
    teachers = Teacher.query.all()
    if len(teachers) <= 0:
        return render_template('index.html')
    else:
        return render_template('quiz.html')


def create_name(data):
    teacher = Teacher(name=data['name'])
    db.session.add(teacher)
    db.session.commit()
    games = Game.query.options(orm.joinedload('*')).all()
    student = Student.query.all()
    if teacher and student and not games:
        game = Game(teacher=teacher, student=student[0])
        db.session.add(game)
        db.session.commit()
    return teacher


def update_question(question: str, identity: int, gameId: int):
    if identity is not 0:
        q = QuestionAnswer.query.filter(QuestionAnswer.id == identity).one()
        q.question = question
    else:
        q = QuestionAnswer(question=question, game_id=gameId)
        db.session.add(q)
    db.session.commit()
    return q


def update_score(score: str, questionId: int):
    questionAnswer = QuestionAnswer.query.filter(QuestionAnswer.id == questionId).one()
    questionAnswer.score = score
    db.session.commit()
    return questionAnswer


def delete_all_data():
    QuestionAnswer.query.delete()
    Game.query.delete()
    Teacher.query.delete()
    Student.query.delete()
    db.session.commit()
    return {"status": "Delete success"}


def event_stream():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(GAME_CHANNEL)
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']


def publish_message(message):
    r.publish(GAME_CHANNEL, message)


def publish_game_data():
    data = {}
    games = Game.query.options(orm.joinedload('*')).all()
    if games:
        data = \
            [dict(g.serializable, student={} if not g.student else g.student.serializable,
                  teacher={} if not g.teacher else g.teacher.serializable,
                  questions=[] if not g.questions else [dict(q.serializable) for q in g.questions])
             for g in games][0]
    publish_message(json.dumps(data))
    db.session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(func=publish_game_data, trigger="interval", seconds=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/name', methods=['POST'])
def save_name():
    return jsonify(create_name(request.get_json()))


@app.route('/question', methods=['POST'])
def save_question():
    question = request.get_json()['question']
    question_id = request.get_json()['id']
    gameId = request.get_json()['gameId']
    return jsonify(update_question(question, question_id, gameId))


@app.route('/score', methods=['POST'])
def save_score():
    question_id = request.get_json()['id']
    score = request.get_json()['score']
    return jsonify(update_score(score, question_id))


@app.route('/end', methods=['POST'])
def end_quiz():
    return jsonify(delete_all_data())


@app.route('/status')
def hello_world():
    return "Hello World"


@app.route('/stream')
def game_stream():
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
