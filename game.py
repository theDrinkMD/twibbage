from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gameIdGenerator import createNewGameId
from models import Game, Player, Player_Answers, Question
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import dbManager
import logging
import gameManager
import messageSender
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
db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def twibbage_game():

    #INITIALIZE
    from_number = request.values.get('From', None)
    msg_body = request.values.get('Body', None)
    lcase_msg_body = ''

    if from_number is not None and msg_body is not None:
        lcase_msg_body = unicode.encode(msg_body.lower())
        lcase_msg_body = lcase_msg_body.strip()

        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
        AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
        #Gamestate Variables for testing
        already_in_game = True
        current_question_id = 1
        max_questions = 4
        max_players = 2
        game_state = "fakeanswertime"
        response_string = ""
        points_for_correct_guess = 200
        points_for_fakeout = 100

        resp = MessagingResponse()
        #resp.message("something is wrong")
        if lcase_msg_body.startswith("newgame"):
            #checkGameState(from_number) or checkInGame()
            #  Check if from number is already in a game.
            if dbManager.checkIfMdnInGame(from_number) == 2:
                response_string = "You're already in a game. To exit that game, respond with \"exitgame\""
            else:
                #lets parse the message and get the max_players and max questions
                game_settings = msg_body.split()

                try:
                    max_questions = int(game_settings[1])
                    print("{} requested a max number of questions of {}".format(from_number, max_questions))
                except IndexError:
                    max_questions = 3
                    print("{} Did not request a maximum number of questions, defaulting to {}".format(from_number, max_questions))

                try:
                    max_players = int(game_settings[2])
                    print("{} requested a max number of players of {}".format(from_number, max_players))
                except IndexError:
                    max_players = 3
                    print("{} Did not request a maximum number of questions, defaulting to {}".format(from_number, max_players))

                #max_questions = msg_body[9:9]
                #max_players = msg_body[11:]

                #createGame(from_number, num_questions)
                new_game = gameManager.createGame(from_number, max_questions, max_players)

                # creates a new game object, returns
                #gameId = "A1B2"
                response_string = "\r Starting a new game... \r - Game ID: {} \r - {} Questions \r - {} Players. " \
                                 "\r Tell your so-called friends to text {} to this number to join. Text rules for... rules.".format(new_game, max_questions, max_players, new_game)

                #send rules to host.
                #gameManager.sendRules(from_number)
        elif lcase_msg_body.startswith("exitgame"):
            print("********** {} requested to exit the game. Removing player from game.".format(from_number))
            #call exitGame(from_number) which should remove the person from a game
            player_id = gameManager.removePlayerFromGame(from_number)
            #now lets double check to make sure that this person Wasn't the game host.
            #dbManager.updateGameState()
            if player_id != 0:
                #Check to see if the player ID is a host of an active game
                if dbManager.isActiveHost(player_id):
                    print("********** {} was game host. Fully ending the game.".format(from_number))
                    ended_game = gameManager.endGameByPlayer(player_id)
                    response_string = "You have been removed. You were host and ended game too."
                else:
                    response_string = "You have been removed from your current game. Bye!"
            else:
                response_string = "You asked to be removed, but we couldn't find you!"
        elif (lcase_msg_body.startswith("rules") or lcase_msg_body.startswith("info")):
                #send rules to host.
                gameManager.sendRules(from_number)
        else:
            # So it's not a new game, which means this can be one of 4 things
            #1. First we should check to see if the person is in a game
            usr_status = dbManager.checkIfMdnInGame(from_number)

            #if the user is either not found, or found, but not in a game,
            #lets see what they've written
            if usr_status == 0 or usr_status ==1:
                #we assume the person is joining a game, so lets get the first 5 bytes
                response_string = gameManager.handleGameJoin(msg_body[:5].upper(),usr_status,from_number)
                #gameManager.sendRules(from_number)
                #ITS AT THIS POINT WELL WANT TO CHECK TO SEE HOW MANY PLAYERS ARE NOW IN ONCE IVE Joined
                my_game = dbManager.getActiveGameByPlayerNumber(from_number)
                max_players = my_game.max_players
                my_game_token = my_game.game_id
                my_game_id = my_game.id

                player_diff = max_players - dbManager.getPlayerCount(my_game_token)
                if player_diff == 0 :
                    #holy shit it is timeee
                    resp.message(response_string)
                    response_string = "OHHH YEAH We're READY TO START THE GAME"
                    gameManager.startGame(my_game_id)

                #if we've joined, and we're now the last player, then lets start the game
            else:
                #lets get this person's game object.
                my_game = dbManager.getActiveGameByPlayerNumber(from_number)
                max_players = my_game.max_players
                my_game_token = my_game.game_id
                my_player = dbManager.getPlayerByMdn(from_number)

                #if we're here, then there are 3 possibilities for game state
                #1. In The Lobby
                if my_game.game_state == "lobby" :
                    # Still waiitng for pepole to join something = 1
                    player_diff = max_players - dbManager.getPlayerCount(my_game_token)
                    response_string = "\r Still waiting for {} player(s). Text rules for... rules".format(player_diff)
                    # Store off their fake answer in a DB with Question #, Game ID, from_number, realAnswer ==false
                elif my_game.game_state == "fakeanswers":
                    #if it is fake answer time, we should be expecting questions here. So we'll want to store off people's answers
                    # 0. First lets make sure that I haven't already answered this question
                    print("Player About to Answer - My current q seq: {}".format(str(my_game.current_question_sequence_number)))
                    if dbManager.checkIfPlayerAlreadyAnswered(my_game.id, my_game.current_question_sequence_number,my_player.id):
                        print("Player Already Answered - My current q seq: {}".format(str(my_game.current_question_sequence_number)))
                        response_string = "You already answered!"
                    else:
                        #print("Not Yet Answered - My current q seq: {}".format(str(my_game.current_question_sequence_number)))
                        #Check if person faked the right answer like a jerkface
                        if gameManager.fakeAnswerIsRealAnswer(my_game.current_question_id, lcase_msg_body):
                            response_string = "Well done hotshot... You selected the correct answer. Please reply with a FAKE answer..."
                            print("{} tried faking the correct answer...".format(from_number))
                        else:
                            print("")
                            # 1. Store off fake answer
                            dbManager.addPlayerAnswer(my_game.id, my_game.current_question_sequence_number,my_player.id,lcase_msg_body)
                            response_string = "Thanks for your fake answer! Waiting for other Players to enter theirs"

                            #2. Check if I'm the last to answer
                            answer_count = dbManager.checkNumberPlayerAnswers(my_game.id,my_game.current_question_sequence_number)
                            player_count = dbManager.getPlayerCount(my_game_token)
                            answers_missing = player_count - answer_count

                            print("answers missing: " + str(answers_missing))
                            #   If I'm last to answer,
                            if answers_missing == 0:
                                gameManager.moveToGuessTime(my_game.id)

                elif my_game.game_state == "guesstime" :
                    #Get a person's Guess and store a person's guess
                    player_guess = msg_body

                    #check if the person already answered
                    if dbManager.checkIfPlayerAlreadyGuessed(my_game.id, my_game.current_question_sequence_number,my_player.id):
                        print("Player Already Guessed - My current q seq: {}".format(str(my_game.current_question_sequence_number)))
                        response_string = "\r You already Guessed!"
                    else:
                        #So this person hasn't submitted a valid guess yet...
                        #0. Lets get my curent player answer
                        my_player_answer = dbManager.getPlayerAnswer(my_game.id, my_game.current_question_sequence_number,my_player.id)

                        #If no, give the person Whos response was selected, a point
                        guessed_player_answer = dbManager.getPlayerAnswerByGuessId(my_game.id, my_game.current_question_sequence_number, player_guess[:1])

                        #is this person being an ass?
                        if lcase_msg_body == my_player_answer.fake_answer_guess_id:
                            response_string = "Come on now, you can't guess your own answer. Please sumbit another answer."
                        #is this an invalid answer?
                        elif lcase_msg_body.isdigit() == False:
                            response_string = "You just need to enter the NUMBER of the guess you wish to make. Try again. Like 1, or maybe 2!"

                        #Is this not even a valid response number?
                        elif guessed_player_answer is None:
                            response_string = "You selected an invalid answer. Sry Bro"
                        else:

                            #1. Finally... we can Store off guess
                            dbManager.updatePlayerAnswerGuess(my_player_answer.id, player_guess)

                            #Is this person's guess the right answer?
                            if dbManager.checkIfGuessRightAnswer(my_game.current_question_id, player_guess):
                                dbManager.updatePlayerScore(my_player.id, points_for_correct_guess)
                                messageSender.sendMessage(from_number, "\r Yay you got it correct! +{} points!".format(str(points_for_correct_guess)))
                            else:

                                dbManager.updatePlayerScore(guessed_player_answer.player_id, points_for_fakeout)
                                #message guesser saying "WRONG"
                                messageSender.sendMessage(from_number, "\r WRONG! You guessed someone else's fake answer!")
                                guessed_player_answer_mdn = dbManager.getPlayerMdnById(guessed_player_answer.player_id)
                                #message faker saying someone guessed your shit! +x Points
                                messageSender.sendMessage(guessed_player_answer_mdn, "HAHAHAHA. {} guessed your answer! +{} for fakeout!".format(from_number,points_for_fakeout))


                            #now lets check whether i was the last to answer, then send scoreboard, and shift Gamestate
                            num_guesses = dbManager.getTotalGuesses(my_game.id,my_game.current_question_sequence_number)
                            total_players = dbManager.getPlayerCount(my_game_token)

                            if num_guesses == total_players:
                                #its time to change game state and send out results of the round
                                gameManager.sendResults(my_game.id)
                                game_continuing = gameManager.nextRound(my_game.id)
                                if not game_continuing:
                                    response_string = "GAME OVER"
                                else:
                                    response_string = ""
                            else:
                                #do nothing really - we're still waiting on other people
                                response_string = "Waiting for others to guess..."
    else:
        response_string = ""
        return("<h1>Welcome to Twibbage</h1><br/><p>To play, text newgame q p to the number, whwere q is the number of quesitons, and p is the number of players you want in a game.</p>")

    #finally, respond.
    resp.message(response_string)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
