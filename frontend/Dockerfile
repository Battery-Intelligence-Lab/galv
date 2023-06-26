# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

FROM node:lts@sha256:132309f5136555725debd57b711eb4b329fff22a00588834dbec391a3f9782cf as build

ARG VIRTUAL_HOST_ROOT="localhost"
ARG FORCE_HTTP=""

RUN mkdir -p /app
WORKDIR /app
COPY package.json yarn.lock /app/

# Required to get react running:
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN yarn install

COPY . /app
ENV VIRTUAL_HOST_ROOT=$VIRTUAL_HOST_ROOT
ENV FORCE_HTTP=$FORCE_HTTP
RUN ["/bin/sh", "-c", "./inject_envvars.sh"]
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY --from=build /app/nginx.conf.template /etc/nginx/conf.d/conf

EXPOSE 80
CMD ["/bin/sh" , "-c" , "exec nginx -g 'daemon off;'"]

