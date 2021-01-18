FROM python


# COPY ./galvanalyser/__init__.py /usr/src/app/galvanalyser/__init__.py
COPY ./galvanalyser/harvester/requirements.txt /usr/

RUN pip install -r /usr/requirements.txt

COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
RUN pip install /usr/src/app/galvanalyser/database

WORKDIR /usr/src/app/galvanalyser/harvester

CMD ["python", "harvester.py"]
