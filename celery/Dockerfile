FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /celery/requirements.txt

WORKDIR /celery

RUN pip install -r requirements.txt

COPY . /celery

CMD [ "celery", "-B", "-A", "tasks:celery", "worker", "--loglevel=INFO", "--concurrency=10" ]
