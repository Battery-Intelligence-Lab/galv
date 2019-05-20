FROM python

WORKDIR /usr/src/app/config

COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
COPY ./galvanalyser/harvester /usr/src/app/galvanalyser/harvester

RUN pip install -r /usr/src/app/galvanalyser/harvester/requirements.txt

CMD ["python", "/usr/src/app/galvanalyser/harvester/harvester.py"]
