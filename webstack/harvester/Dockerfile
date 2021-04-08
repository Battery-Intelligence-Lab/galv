FROM python

COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
RUN pip install -e /usr/src/app/galvanalyser/database

COPY ./galvanalyser/harvester /usr/src/app/galvanalyser/harvester
RUN pip install -e /usr/src/app/galvanalyser/harvester

WORKDIR /usr/src/app/galvanalyser/harvester

CMD ["python", "-m", "harvester"]

