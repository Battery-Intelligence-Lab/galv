FROM python

COPY ./galvanalyser/webapp/requirements.txt /usr/requirements.txt
COPY libs/galvanalyser-dash-components/dist/galvanalyser_dash_components-*.tar.gz /usr/galvanalyser_dash_components.tar.gz

RUN pip install -r /usr/requirements.txt && \
    pip install /usr/galvanalyser_dash_components.tar.gz

COPY ./galvanalyser/database /usr/src/app/galvanalyser/database
RUN pip install /usr/src/app/galvanalyser/database

EXPOSE 8050
