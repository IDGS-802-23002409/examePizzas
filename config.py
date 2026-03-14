import os

class Config:
    SECRET_KEY = 'pizzas-secreto-123'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/pizzas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
