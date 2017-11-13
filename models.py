from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twibbage_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Game(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(5))
    game_state = db.Column(db.String(12))
    number_of_questions = db.Column(db.Integer)
    current_question_sequence_number = db.Column(db.Integer)
    current_question_id = db.Column(db.Integer)
    creator_user_id = db.Column(db.Integer)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    max_players = db.Column(db.Integer)

    def __init__(self,game_id=None, game_state=None,number_of_questions=None,current_question_sequence_number=None,current_question_id=None, creator_user_id=None, max_players=None):
        self.game_id = game_id
        self.game_state = game_state
        self.number_of_questions = number_of_questions
        self.current_question_sequence_number = current_question_sequence_number
        self.current_question_id = current_question_id
        self.creator_user_id = creator_user_id
        self.max_players = max_players

    def __repr__(self):
        return '%r' % (self.id)

class Player(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(5))
    mdn = db.Column(db.String(12))
    score = db.Column(db.Integer)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self,game_id=None, mdn=None,score=None):
        self.game_id = game_id
        self.mdn = mdn
        self.score = score

    def __repr__(self):
        return '%r' % (self.id)

class Player_Answers(db.Model):
    __tablename__ = "player_answers"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(5))
    question_sequence_number = db.Column(db.Integer)
    player_id = db.Column(db.Integer)
    fake_answer = db.Column(db.String(255))
    guess = db.Column(db.String(255))
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fake_answer_guess_id = db.Column(db.String(3))

    def __init__(self,game_id=None, question_sequence_number=None, player_id=None,fake_answer=None,guess=None, fake_answer_guess_id=None):
        self.game_id = game_id
        self.question_sequence_number = question_sequence_number
        self.player_id = player_id
        self.fake_answer = fake_answer
        self.guess = guess
        self.fake_answer_guess_id = fake_answer_guess_id

    def __repr__(self):
        return '%r' % (self.id)

class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(5))
    question_sequence_number = db.Column(db.Integer)
    question = db.Column(db.String(255))
    true_answer = db.Column(db.String(255))
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    real_answer_guess_id = db.Column(db.String(3))

    def __init__(self,game_id=None, question_sequence_number=None, question=None,true_answer=None,real_answer_guess_id=None):
        self.game_id = game_id
        self.question_sequence_number = question_sequence_number
        self.question = question
        self.true_answer = true_answer
        self.real_answer_guess_id = real_answer_guess_id

    def __repr__(self):
        return '%r' % (self.id)
