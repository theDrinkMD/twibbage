# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gameIdGenerator import createNewGameId
from models import Game, Player, Player_Answers, Question
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twibbage_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def doAClassthing():
    #gameRecord = Game()
    #gameRecord = Game("ABCD", "lobby", 3, 1, 1, 3,4)
    #newPlayer = Player()
    #newPlayer = Player("ABCD", "+16106083377",0)
    #newQuestion = Question()
    #newQuestion = Question("ABCD", 1, "Who is your daddy and what does he do?", "Michael. Technology.")
    game = Game.query.filter(Game.game_id == 'ABCD').first()
    resp = MessagingResponse()
    resp.message("Id = {}\r game_id = {}\r game_state ={}\r".format(game.id,game.game_id,game.game_state) +
                "number_of_questions={}\r".format(game.number_of_questions))
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
