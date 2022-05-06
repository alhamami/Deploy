import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgres://zbnlxtmlovaaus:808b773adf253882212303c1a23964fa5b5b621ab55ff177d53036ed6cf02d51@ec2-52-1-20-236.compute-1.amazonaws.com:5432/d1j3kdp6fvuehv/Analysight'
SQLALCHEMY_TRACK_MODIFICATIONS = False