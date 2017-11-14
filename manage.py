from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os
from os.path import join, dirname
from dotenv import load_dotenv

app = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PRODUCTION_DATABASE_URL = os.environ.get("PRODUCTION_DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION_DATABASE_URL

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

if __name__ == '__main__':
    manager.run()
