FROM python


COPY ./galvanalyser/__init__.py /usr/src/app/galvanalyser/__init__.py
COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
COPY ./galvanalyser/harvester /usr/src/app/galvanalyser/harvester

RUN pip install -r /usr/src/app/galvanalyser/harvester/requirements.txt

WORKDIR /usr/src/app/

CMD ["python", "-m", "galvanalyser.harvester.harvester"]
