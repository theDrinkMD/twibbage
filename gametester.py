# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gameIdGenerator import createNewGameId
from models import Game, Player, Player_Answers, Question
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import dbManager
import logging
import urllib2
import json
import gameManager
import questionGenerator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twibbage_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def formatFromText(f, bdy):
    stringy = "From Number: {}\rBody: {}".format(f, bdy)
    return stringy

def updatePlayerGameId2(mdn_to_update, new_game_id, gm_id, new_state):
    #plr = Player()
    #plr = Player.query.filter(Player.mdn==mdn_to_update).first()
    plr = db.session.query(Player).filter(Player.mdn==mdn_to_update).first()

    if plr is not None:
        app.logger.error("The new Game ID is: {}".format(new_game_id))
        app.logger.error("The old Game ID is: {}".format(plr.game_id))
        plr.game_id = new_game_id

        app.logger.error("New Player.game_id{}".format(plr.game_id))
        db.session.commit()

        gm = db.session.query(Game).filter(Game.id==gm_id).first()
        gm.game_state = new_state
        db.session.commit()

        plr2 = Player.query.filter(Player.mdn==mdn_to_update).first()
        app.logger.error("New Player.game_id{}".format(plr2.game_id))
        #db.session.close()
        #db.session.close()
        return plr.id
    else:
        return 0

@app.route("/", methods=['GET', 'POST'])
def doAClassthing():
    output_test = "butts"
    #gameRecord = Game()
    #gameRecord = Game("ABCD", "lobby", 3, 1, 1, 3,4)
    #app.logger.info(str(request))
    #print request.__dict__

    #from_number = request.values.get('From', None)
    #msg_body = request.values.get('Body', None)
    #lcase_msg_body = msg_body.lower()
    #app.logger.info("From:{}, Body:{}".format(from_number, msg_body))

    #---UPDATE PLAYER Answer
    #dbManager.updatePlayerAnswerFakeGuessId(pa_id, fk_ans_g_id)
    #dbManager.updateQuestionRealAnswerGuessId(q_id, rag_id)
    #dbManager.updatePlayerAnswerGuess(14, None)

    #--- Update Game Sequence
    #dbManager.updateGameSequenceNumber(14, 0)

    #---UPDATE GAME STATE
    dbManager.updateGameState(27, "complete")

    #dbManager.updateGameQuestionId(14, 27)

    #dbManager.updatePlayerScore(2, -300)
    #gameManager.nextRound(25)
    #---Start Game Tester
    #gameManager.startGame(12)
    st=""
    #---JSON STUFF-----
    #json_string = urllib2.urlopen("http://www.jservice.io/api/random?count=10").read()
    #app.logger.info("JSON: {}\r".format(json_string))

    #----Count Tester
    #st = str(dbManager.getPlayerCount("93B6J"))
    #parsed_json = json.loads(json_string)
    #for i in range (0,10):
    #    app.logger.info("Question: {}".format(parsed_json[i]["question"]))
    #    app.logger.info("Answer: {}".format(parsed_json[i]["answer"]))
    #game_seq_number = questionGenerator.generateAndSaveQuestions("XEKH3",3)
    #app.logger.info("id of first question: {}".format(game_seq_number))
    #app.logger.info("Answer: {}\r".format(parsed_json[0]["answer"]))

    #plr_id = dbManager.updatePlayerGameId(from_number, "ABCD", 4, "lobby")
    #plr_id = updatePlayerGameId2("+14087687080", "XEKH3", 9, "lobby")
    #plr_id = updatePlayerGameId2("+14087687080", "XEKH3", 9, "lobby")
    #if plr_id != 0:
    #    st = "Player Updated"
    #else:
        #st = "player not updated"
    # -- Remove All Players
    #st = ""
    #players_removed = dbManager.removeAllPlayersFromGame(9)
    #for player in players_removed:
        #app.logger.info("id:{}, mdn:{}".format(player.id, player.mdn))
        #st = "{}\r".format(st)

    #if dbManager.checkGameExists(msg_body):
    #    st = "Exists"
    #else:
    #    st = "Doesn't Exist"

    resp = MessagingResponse()
    resp.message(st)
    #resp.message("hi Jon: {}".format(output_test))
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
