FROM python

WORKDIR /usr/src/app

COPY ./galvanalyser/webapp/requirements.txt /usr/requirements.txt
COPY libs/galvanalyser-dash-components/dist/galvanalyser_dash_components-*.tar.gz /usr/galvanalyser_dash_components.tar.gz

RUN pip install -r /usr/requirements.txt && \
    pip install /usr/galvanalyser_dash_components.tar.gz

EXPOSE 8050

CMD ["python", "-m", "galvanalyser.webapp.app"]
