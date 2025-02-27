import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
    SQLALCHEMY_DATABASE_URI = 'postgresql://mehdiabouhane@localhost/language_test_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False