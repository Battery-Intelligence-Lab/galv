FROM python

RUN apt-get update && apt-get install -y postgresql-client

COPY ./galvanalyser/webapp/requirements.txt /usr/requirements.txt
RUN pip install -r /usr/requirements.txt

COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
RUN pip install -e /usr/src/app/galvanalyser/database

COPY ./galvanalyser/harvester /usr/src/app/galvanalyser/harvester
RUN pip install -e /usr/src/app/galvanalyser/harvester

ENV FLASK_APP=app.py

EXPOSE 8050
