FROM python:3.8.2-slim

ENV APP_HOME /app
WORKDIR ${APP_HOME}

COPY . ./

RUN pip install -r requirements.txt \
    && pip install --upgrade pip


RUN chmod 644 ./core/fixtures/Cellar/geckodriver/0.27.0/bin/geckodriver

ADD . .


CMD gunicorn score_predictor.wsgi:application --bind 0.0.0.0:$PORT
