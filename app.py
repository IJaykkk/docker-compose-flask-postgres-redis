import os
import time
import logging
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import abort, request, jsonify, g

application = Flask(__name__)
application.config.update(
    SQLALCHEMY_DATABASE_URI='postgresql://{}:{}@{}:{}/{}'.format(
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_PORT"],
        os.environ["POSTGRES_DB"]
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SQLALCHEMY_ECHO=False
)
gunicorn_logger = logging.getLogger('gunicorn.error')
application.logger.handlers = gunicorn_logger.handlers
application.logger.setLevel(gunicorn_logger.level)

application.logger.info('env: {} {} {} {} {}'.format(
    os.environ["POSTGRES_USER"],
    os.environ["POSTGRES_PASSWORD"],
    os.environ["POSTGRES_HOST"],
    os.environ["POSTGRES_PORT"],
    os.environ["POSTGRES_DB"]
))

db = SQLAlchemy(application)
cache = redis.Redis(host='redis', port=6379)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True, index=True)

db.create_all()

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@application.route('/')
def get_index():
    count = get_hit_count()
    user = User(username="user{}".format(count))

    try:
        db.session.add(user)
        db.session.commit()
    except AssertionError as err:
        return jsonify(msg='Error: {} '.format(err)), 400
    except:
        return jsonify(msg='Error: Unknown'), 400
    return "Yo! You are the {} th visitor to visit.".format(count), 200

