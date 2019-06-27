FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /service/requirements.txt

WORKDIR /service

RUN pip install -r requirements.txt

COPY . /service

CMD [ "gunicorn", "-b", "0.0.0.0:6000", "app:app" ]
