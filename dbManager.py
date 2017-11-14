from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from models import Player, Game, Player_Answers, Question

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twibbage_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def addGame(game_id, num_quest, user_id, max_players):
    #game_state will initiate with "lobby"
    newGame = Game()
    newGame = Game(game_id, "lobby", num_quest, 0, None, user_id, max_players)
    db.session.add(newGame)
    db.session.flush()
    new_game_id = newGame.id
    db.session.commit()
    #new_game = Game.query.filter(Game.game_id==game_id, Game.game_state == "lobby").first()
    #db.session.close()
    return new_game_id

#Adds a record of a player to a game. And returns the player id.
def addPlayer(game_id, mdn):
    newPlayer = Player()
    newPlayer = Player(game_id, mdn,0)
    db.session.add(newPlayer)
    db.session.commit()
    new_player = db.session.query(Player).filter(Player.mdn==mdn).first()
    #db.session.close()
    return new_player.id

def addQuestion(game_id, seq, question, true_answer):
    newQuestion = Question()
    newQuestion = Question(game_id, seq, question, true_answer)
    db.session.add(newQuestion)
    db.session.flush()
    new_question_id = newQuestion.id
    db.session.commit()
    #db.session.close()
    return new_question_id

def addPlayerAnswer(game_id, seq, player_id, fake_answer):
    newPlayerAnswer = Player_Answers()
    newPlayerAnswer = Player_Answers(game_id,seq,player_id, fake_answer, None)
    db.session.add(newPlayerAnswer)
    db.session.flush()
    new_player_answer_id = newPlayerAnswer.id
    db.session.commit()
    #db.session.close()
    return new_player_answer_id

#**********************************************
# UPDATES
#**********************************************
#not sure what the point of this one is
#def updateGame():
    #
#Here ID is the actual id of the record, not the game name.
#def updateGameState(id, game_state):
#updates the game's current question number ID and Sequence
#def updateGameQuestionNumber(next_q_num):
    #TBD
def updatePlayerGameId(mdn_to_update, new_game_id):
    #plr = Player()
    plr = db.session.query(Player).filter(Player.mdn==mdn_to_update).first()

    if plr is not None:

        print("********** {}'s old Game ID id was: {}".format(mdn_to_update, plr.game_id))
        plr.game_id = new_game_id
        print("********** {}'s new Game ID is: {}".format(mdn_to_update, plr.game_id))
        db.session.commit()

        plr2 = Player.query.filter(Player.mdn==mdn_to_update).first()

        return plr.id
    else:
        return 0

def removeAllPlayersFromGame(g_id):
        game_to_update = db.session.query(Game).filter(Game.id==g_id).first()
        print("Game Token to Update: {}".format(game_to_update.game_id))
        game_token = game_to_update.game_id

        plyrs = db.session.query(Player).filter(Player.game_id==game_token).all()
        for plyr in plyrs:
            print("********** Removing {} from {}".format(plyr.mdn,game_token))
            plyr.game_id = None
            plyr.score = 0
        db.session.commit()
        return plyrs


#Updates Game state of game with id
def updateGameState(id_of_game, new_game_state):
    game_to_update = db.session.query(Game).filter(Game.id==id_of_game).first()
    game_to_update.game_state = new_game_state
    db.session.commit()

def updateGameSequenceNumber(g_id, seq):
    game_to_update = db.session.query(Game).filter(Game.id==g_id).first()
    game_to_update.current_question_sequence_number = seq
    db.session.commit()

def updateGameQuestionId(id_of_game, q_id):
    q_to_update = db.session.query(Game).filter(Game.id==id_of_game).first()
    q_to_update.current_question_id = q_id
    db.session.commit()

def updatePlayerAnswerFakeGuessId(pa_id, fk_ans_g_id):
    player_answer = db.session.query(Player_Answers).filter(Player_Answers.id==pa_id).first()
    player_answer.fake_answer_guess_id = fk_ans_g_id
    db.session.commit()

def updateQuestionRealAnswerGuessId(q_id, rag_id):
    q = db.session.query(Question).filter(Question.id==q_id).first()
    q.real_answer_guess_id = rag_id
    db.session.commit()

def updatePlayerAnswerGuess(pa_id, guess):
    player_answer = db.session.query(Player_Answers).filter(Player_Answers.id==pa_id).first()
    player_answer.guess = guess
    db.session.commit()

def updatePlayerScore(p_id, points):
    plr = db.session.query(Player).filter(Player.id==p_id).first()
    plr.score = plr.score + points
    db.session.commit()

#Looks up a game by ID, then figures out what the next question sequence number is,
#finds the next question based off of game id and next question sequ number. Then updates the game
#object with 1 more in the sequence, and the new question ID.
def updateGameToNextQuestion(g_id):
    print("********** \r Now we're in the updateGameToNextQuestion method... \r")
    g = db.session.query(Game).filter(Game.id==g_id).first()
    nextQuestionSeqId = g.current_question_sequence_number + 1
    print("********** \r next question sequence id: {}".format(str(nextQuestionSeqId)))
    #lets find the next question in the sequence
    q = db.session.query(Question).filter(Question.game_id==g.game_id, Question.question_sequence_number==nextQuestionSeqId).first()
    g.current_question_sequence_number = nextQuestionSeqId
    print("********** \r current question seq number now: {}".format(str(g.current_question_sequence_number)))
    g.current_question_id = q.id
    print("********** \r quest id = {}".format(str(q.id)))
    print("********** \r new curent question id = {}".format(str(g.current_question_id)))
    db.session.commit()
    #db.session.close()

#**********************************************
# Gets
#**********************************************
#   gameId, init_mdn, current_question_id, number_of_questions, game_state
def checkGameExists(gmId):
    #Check if an active game exists.
    gameExists = db.session.query(Game).filter(Game.game_id == gmId, Game.game_state != 'complete').first()
    #if game exists is none, that means there are no games, an active game
    #doesn't already exist
    #session.close()
    if gameExists is None:
        return False
    else:
        return True

#checks if the MDN is already in a game
#returns true if... true, false if MDN isn't in a game or hasn't been added to db
def checkIfMdnInGame(mdn_to_check):
    print("********** Checking if {} is already in a game ".format(mdn_to_check))
    plr = db.session.query(Player).filter(Player.mdn == mdn_to_check).first()

    #if plr is None, not in a game, and doesn't exist
    if plr is None:
        return 0
        print("********** Player does not exist in system.")
    #if plr is Not none, and plr has no game ID
    elif plr.game_id is None:
        print("********** Player exists, but is not in an active game.")
        return 1
    #Must exist and has Game ID
    else:
        return 2

def isActiveHost(creator_id):
    g_host = db.session.query(Game).filter(Game.creator_user_id==creator_id, Game.game_state!='complete').first()
    if g_host is not None:
        return True
    else:
        return False

#def getGameCode(game_record_id):
    #return game_id

#def getGameRecordId(game_id):
    #game_record_id =
    #return

def getGameByToken(token):
    #lets make sure what they passed is all upper case, like we store in DB
    u_token = token.upper()
    g_host = db.session.query(Game).filter(Game.game_id==u_token, Game.game_state!='complete').first()
    return g_host

def getGameById(g_id):
    g = db.session.query(Game).filter(Game.id==g_id).first()
    return g

#def getCurrentQuestionSequence(id):

#def getCurrentQuestionId(id):

#def getUserCreatedId(id):

#def getMaxNumberOfQuestions(id):

def getPlayerId(mdn_to_check):
    plr = db.session.query(Player).filter(Player.mdn==mdn_to_check).first()
    if plr is not None:
        return plr.id
    else:
        return None

def getPlayerByMdn(mdn_to_check):
    plr = db.session.query(Player).filter(Player.mdn==mdn_to_check).first()
    return plr

def getPlayerMdnById(p_id):
    p = db.session.query(Player).filter(Player.id==p_id).first()
    return p.mdn

def getActiveGameByPlayerId(plr_id):
    g_host = db.session.query(Game).filter(Game.creator_user_id==plr_id, Game.game_state!='complete').first()
    return g_host.id

def getActiveGameByPlayerNumber(mdn):
    p = db.session.query(Player).filter(Player.mdn==mdn).first()
    gt = p.game_id
    active_game = db.session.query(Game).filter(Game.game_id==gt, Game.game_state!='complete').first()
    return active_game

def getPlayerCount(game_token):
    p = db.session.query(Player).filter(Player.game_id==game_token).count()
    return p

def getPlayersByGameToken(game_token):
    p = db.session.query(Player).filter(Player.game_id==game_token).all()
    return p

def getPlayersByGameId(g_id):
    g = db.session.query(Game).filter(Game.id==g_id).first()
    players = db.session.query(Player).filter(Player.game_id==g.game_id).all()
    return players

def getPlayersByGameIdScoreDesc(g_id):
    g = db.session.query(Game).filter(Game.id==g_id).first()
    players = db.session.query(Player).filter(Player.game_id==g.game_id).order_by(Player.score.desc()).all()
    return players

def getWinningPlayer(g_id):
    g = db.session.query(Game).filter(Game.id==g_id).first()
    player = db.session.query(Player).filter(Player.game_id==g.game_id).order_by(Player.score.desc()).first()
    return player

def getQuestion(q_id):
    q = db.session.query(Question).filter(Question.id==q_id).first()
    return q

def getQuestionById(q_id):
    q = db.session.query(Question).filter(Question.id==q_id).first()
    return q.question

def getGameQuestionIdByGameId(g_id):
    g = db.session.query(Game).filter(Game.id==g_id, Game.game_state!='complete').first()
    return g.current_question_id

#note here, i'm typecasting the g_id to string because the game_id field is
#actually a string in the db type
def checkIfPlayerAlreadyAnswered(g_id,seq,plr_id):
    player_answer = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq,Player_Answers.player_id==plr_id).first()
    if player_answer is not None:
        return True
    else:
        return False

#note here, i'm typecasting the g_id to string because the game_id field is
#actually a string in the db type
def checkIfPlayerAlreadyGuessed(g_id,seq,plr_id):
    player_answer = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq,Player_Answers.player_id==plr_id).first()
    if player_answer is not None:
        return True
    else:
        return False

def checkNumberPlayerAnswers(g_id,seq):
    count = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq).count()
    return count

def getPlayerAnswers(g_id,seq):
    ans = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq).all()
    return ans

def getPlayerAnswer(g_id,seq,plr_id):
    pa = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq,Player_Answers.player_id==plr_id).first()
    return pa

def checkIfGuessRightAnswer(q_id, guess):
    q = db.session.query(Question).filter(Question.id==q_id).first()
    if q.real_answer_guess_id == guess[:1]:
        return True
    else :
        return False

def getPlayerAnswerByGuessId(g_id,seq,guess):
    pa = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq,Player_Answers.fake_answer_guess_id==guess).first()
    return pa

def getTotalGuesses(g_id,seq):
    count = db.session.query(Player_Answers).filter(Player_Answers.game_id==str(g_id),Player_Answers.question_sequence_number==seq, Player_Answers.guess!=None).count()
    return count
