FROM python

WORKDIR /usr/src/app

COPY ./galvanalyser/webapp/requirements.txt /usr/requirements.txt

RUN pip install -r /usr/requirements.txt

EXPOSE 8050

CMD ["python", "app.py"]
