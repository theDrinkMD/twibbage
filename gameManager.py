import gameIdGenerator
import dbManager
import models
import logging
import json
import questionGenerator
import messageSender
from twilio.rest import Client
from flask import Flask, request
import random
import os
from os.path import join, dirname
from dotenv import load_dotenv

app = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PRODUCTION_DATABASE_URL = os.environ.get("PRODUCTION_DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION_DATABASE_URL
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twibbage_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def createGame(mdn, number_of_questions, max_players, player_alias):
    # 1. Call subroutine to create a random Game ID
    #assume the game already exists
    # 2. Check to see if that game id exists, if so do it again,
    # and check again. we'll only hop out of here if gameExists becomes
    #False
    gameExists = True
    while gameExists:
        game_token = gameIdGenerator.createNewGameId()
        gameExists = dbManager.checkGameExists(game_token)

    # 3. We first must add the player, so we have the player ID who created the game
    #3.1 Lets first check to see if the player already has a record.
    if dbManager.getPlayerId(mdn) is None:
        player_id = dbManager.addPlayer(game_token, mdn, player_alias)
    else:
        #3.2 Player already exists, so we need to update his game id
        player_id = dbManager.updatePlayerGameId(mdn, game_token)
    # 4. Now that we have a player_id, create a game!
    #addGameToDb(game_id, "lobby", number_of_questions, 1, Null, player_id)
    game_id = dbManager.addGame(game_token, number_of_questions, player_id, max_players)

    #lets generate some questions
    first_question_id = questionGenerator.generateAndSaveQuestions(game_token,number_of_questions)

    #lets update the game record we created
    dbManager.updateGameQuestionId(game_id, first_question_id)
    # 5. YAY Game created! tell the sub who called it what the game id is

    # Lets get questions for the game
    return game_token

def removePlayerFromGame(mdn):
    #basically all we do here is set the game_id of the player record to None
    plr_id = dbManager.updatePlayerGameId(mdn, None)
    return plr_id

def endGame(game_id_to_end):
    #first lets set game status to "complete"
    dbManager.updateGameState(game_id_to_end, "complete")
    players = dbManager.removeAllPlayersFromGame(game_id_to_end)
    return players
    #Then update all players who are in the game with the
    #For each player in game, int i = 0
    #rmvd_plr_id[i] = removePlayerFromGame(plr.mdn)
    #removed_plrs[] = plr.mdn

def endGameByPlayer(player_id_to_end):
    game_to_end = dbManager.getActiveGameByPlayerId(player_id_to_end)
    endGame(game_to_end)
    return game_to_end

def handleGameJoin(msg,usr_status,from_number,player_alias):
    active_game = dbManager.getGameByToken(msg[:5])
    #get a game object back
    if active_game is None:
        return "We could not find an active game with that code"
    else:
        if (active_game.game_state == "lobby"): #ADD CODE TO CHecK NUM Players
            if usr_status == 0:
                #need to add player to db with active game
                player_id = dbManager.addPlayer(active_game.game_id, from_number,player_alias)
                return "We have added you to the game! Thanks for joining! Text Rules for... rules."
            else:
                player_id = dbManager.updatePlayerGameId(from_number,active_game.game_id)
                if player_alias != from_number:
                    dbManager.updatePlayerAlias(from_number, player_alias)
                return "We have added you to the game. Thanks for coming back! Text Rules for... rules."
        else:
            return "Game is not joinable."

def startGame(g_id):
    #update game state
    dbManager.updateGameState(g_id,"fakeanswers")

    #get question
    question_1 = dbManager.getQuestionById(dbManager.getGameQuestionIdByGameId(g_id))
    instruction = "... \r Supply a fake answer for others to guess."
    #get player
    players = dbManager.getPlayersByGameId(g_id)
    current_q_num = 1 + dbManager.getGameQuestionSequenceNumber(g_id)

    for player in players:
        messageSender.sendMessage(player.mdn, "Question {}: \r".format(current_q_num) + question_1 + "{}".format(instruction))
        print("********** {}. Sent to {}".format(question_1, player.mdn))

def moveToGuessTime(g_id):
    print("Moved To Guess Time")
    #Get Game Info by id
    curr_game = dbManager.getGameById(g_id)

    #Get All Answers from Table
    answers = dbManager.getPlayerAnswers(g_id, curr_game.current_question_sequence_number)

    #Build Response message
    str_response = "\r The following answers were given: \r"
    anum = 1

    #Also lets get the real answer
    curr_question = dbManager.getQuestion(curr_game.current_question_id)
    real_answer = curr_question.true_answer

    #first lets actually generate a random number between 1 and total num of answers
    rndNum = random.randint(1,len(answers))

    #lets loop through all the answers to...
    #1. Assign a numerical value to an answer (true and fake)
    #2. Create a response string
    for answer in answers:
        #if our anum variable = the random number, thats where we are going to insert
        #the real answer.
        if rndNum == anum:
            str_response = str_response + "{}. {}\r".format(anum, real_answer.lower())
            #lets store off the value that people will have to enter to select the right answer
            dbManager.updateQuestionRealAnswerGuessId(curr_question.id, str(anum))
            anum = anum + 1

        str_response = str_response + "{}. {}\r".format(anum, answer.fake_answer)
        dbManager.updatePlayerAnswerFakeGuessId(answer.id, str(anum))
        anum = anum + 1

    str_response = str_response + "\r Reply with the answer number you think is correct."
    #K lets get the list of players
    players = dbManager.getPlayersByGameId(g_id)

    #Send Message With Question and Fake Answers
    for player in players:
        messageSender.sendMessage(player.mdn, str_response)


    #Update game state
    dbManager.updateGameState(g_id, "guesstime")

def sendResults(g_id):
    #get game
    curr_game = dbManager.getGameById(g_id)

    #get players & scores
    players = dbManager.getPlayersByGameId(g_id)

    str_response = "\r And the scores after the last round are: \r"
    #Build response.
    for player in players:
        str_response = str_response + "{} - {}\r".format(player.player_name, str(player.score))
        #str_response = str_response + "{} - {}\r".format(player.mdn, str(player.score))

    #Send Response
    for play in players:
        messageSender.sendMessage(play.mdn, str_response)

def moveToFakeAnswer(g_id):
    #update game state
    dbManager.updateGameState(g_id,"fakeanswers")

    #Game Object should already be updated
    game_q_id = dbManager.getGameQuestionIdByGameId(g_id)
    current_q_num = 1 + dbManager.getGameQuestionSequenceNumber(g_id)

    print("moving to fake answers - the next question id is {}".format(str(game_q_id)))
    #get question
    next_question = dbManager.getQuestionById(game_q_id)
    print("mving to fake answers - next q is {}".format(next_question))

    instruction = "... \r Reply with a fake answer for others to guess."

    #get player
    players = dbManager.getPlayersByGameIdScoreDesc(g_id)

    for player in players:
        messageSender.sendMessage(player.mdn, "Question {}: \r".format(current_q_num) + next_question + "{}".format(instruction))
        print("********** {}. Sent to {}".format(next_question, player.mdn))


def nextRound(g_id):
    print("********** attempting to move to next round...")
    #get game
    cGame = dbManager.getGameById(g_id)
    nextSeqNum = cGame.current_question_sequence_number + 1
    print("********** nextSeqNum is {}".format(str(nextSeqNum)))
    #getPlayersByGameId
    players = dbManager.getPlayersByGameId(g_id)

    #check if there are more questions
    if nextSeqNum < cGame.number_of_questions:
        print("********** I'm in Next Round and my seq number before updating is {}".format(str(cGame.current_question_sequence_number)))

        # more questions...
        # lets update the Game's... sequence_number_and_question ID automatically ahndled by
        # updateGameToNextQuestion
        dbManager.updateGameToNextQuestion(g_id)

        #Lets update the gamestate and send out next question
        moveToFakeAnswer(g_id)
        return True
    else:
        # build final message
        endGame2(g_id)
        return False


def endGame2(g_id):
    #get game
    curr_game = dbManager.getGameById(g_id)

    #get players in order of score desc.
    winning_plr = dbManager.getWinningPlayer(g_id)

    #get players & scores
    players = dbManager.getPlayersByGameId(g_id)
    #Build Response message
    resp_msg = "\r Congratulations to {}, winning with a score of {} points!!!! Thanks for playing!".format(winning_plr.mdn, winning_plr.score)

    #Send Final Messsage
    for play in players:
        messageSender.sendMessage(play.mdn, resp_msg)

    #Update Game state
    dbManager.updateGameState(g_id,"complete")

    #removeAllPlayersFromGame
    rmvd_plyers = dbManager.removeAllPlayersFromGame(g_id)

def sendRules(mdn):
    rules_string = "\r Rules: \r - All players are asked a question. \r " \
                   "- Respond with a made-up answer that you think other people would think is the real answer. \r" \
                   "- You will then receive a list of all fake answers + the real answer. \r" \
                   "- Guess the real answer by entering its number. \r" \
                   "- +200 points for guessing correct answer, +100 points for every time someone guesses your fake answer."
    messageSender.sendMessage(mdn, rules_string)

def sendInstruction(mdn, game_token):
    instruction_string = "\r Tell your socalled friends to text {} to this number to join.".format(game_token)
    messageSender.sendMessage(mdn, instruction_string)

def fakeAnswerIsRealAnswer(q_id, fk_ans):
    question = dbManager.getQuestion(q_id)
    real_answer = question.true_answer
    real_answer = real_answer.strip()
    fake_answer = fk_ans.strip()
    real_answer = real_answer.lower()
    fake_answer = fake_answer.lower()

    if real_answer == fake_answer:
        return True
    elif real_answer[:2] == "a " or fake_answer[:2] == "a " or real_answer[:4] == "the " or fake_answer[:4] == "the " :
        if real_answer[:2] == "a ":
            real_compare = real_answer[2:]
        elif real_answer[:4] == "the ":
            real_compare = real_answer[4:]
        else:
            real_compare = real_answer

        if fake_answer[:2] == "a ":
            fake_compare = fake_answer[2:]
        elif fake_answer[:4] == "the ":
            fake_compare = fake_answer[4:]
        else:
            fake_compare = fake_answer

        if fake_compare == real_compare:
            return True
        else:
            return False
    else:
        return False
