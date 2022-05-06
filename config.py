import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:o0kARjWrSUxAcv61DyEM@containers-us-west-50.railway.app:5714/railway'
SQLALCHEMY_TRACK_MODIFICATIONS = False
