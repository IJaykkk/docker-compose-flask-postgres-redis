import os
from app import app
from flask_sqlalchemy import SQLAlchemy


app.config.update(
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

db = SQLAlchemy(app)
