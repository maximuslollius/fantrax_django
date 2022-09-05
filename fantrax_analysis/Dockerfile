FROM python:3.8.2-slim

ENV APP_HOME /app
WORKDIR ${APP_HOME}

COPY . ./

RUN pip install -r requirements.txt \
    && pip install --upgrade pip

ADD . .

CMD gunicorn score_predictor.wsgi:application --bind 0.0.0.0:$PORT
