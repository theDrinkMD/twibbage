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
import urllib3
import json
import gameManager
import questionGenerator

app = Flask(__name__)

def generateAndSaveQuestions(game_id, number_of_questions):
        query_string = "http://www.jservice.io/api/random?count={}".format(number_of_questions)
        #json_string = urllib2.urlopen(query_string).read()
        http = urllib3.PoolManager()
        json_string = http.request("GET",  query_string)
        print("Getting questions and getting answers begrudgingly from Trebek...")

        #parsed_json = json.loads(json_string)
        parsed_json = json.loads(json_string.data)
        for i in range (0,number_of_questions):
            #Add question to the DB
            question_id = dbManager.addQuestion(game_id, i, parsed_json[i]["question"],parsed_json[i]["answer"])
            print("********** Question: {}".format(parsed_json[i]["question"]))
            print("********** Answer: {}".format(parsed_json[i]["answer"]))
            if i ==0:
                starting_question_id = question_id

        return starting_question_id
