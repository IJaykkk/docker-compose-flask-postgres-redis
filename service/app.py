import time
import logging
from flask import Flask, abort, request, jsonify, g
import celery.states as celery_states

app = Flask(__name__)

# logger
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

from db import db
from broker import redis
from worker import celery


# Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True, index=True)

db.create_all()


def get_hit_count():
    retries = 5
    while True:
        try:
            return redis.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
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
    return "Yo! You are the {} th visitor to visit.\n".format(count), 200


@app.route('/add/<int:x>/<int:y>')
def add(x, y):
    task = celery.send_task('tasks.add', args=[x, y], kwargs={})
    response = "check status of {}\n".format(task.id)
    return response, 200


@app.route('/check/<string:task_id>')
def check_task(task_id):
    res = celery.AsyncResult(task_id)
    if res.state == celery_states.PENDING:
        return res.state
    else:
        return "{}\n".format(res.result)
