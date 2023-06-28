# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

FROM python:3.10.4-slim@sha256:a2e8240faa44748fe18c5b37f83e14101a38dd3f4a1425d18e9e0e913f89b562

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install postgresql-client for healthchecking
#RUN apt-get update && \
#    apt-get install -y \
#    	postgresql-client \
#    	build-essential libssl-dev libffi-dev python3-dev python-dev && \
#    apt-get autoremove && \
#    apt-get autoclean

RUN mkdir -p /usr/harvester
WORKDIR /usr/harvester
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . /usr/harvester
