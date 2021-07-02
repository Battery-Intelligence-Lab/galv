FROM python

RUN mkdir -p /usr/app
WORKDIR /usr/app

RUN apt-get update && apt-get install -y postgresql-client

COPY . . 
RUN pip install -e . 

ENV FLASK_APP=app.py

EXPOSE 8050
