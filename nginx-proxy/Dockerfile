FROM jwilder/nginx-proxy:1.3.1
COPY ./default /etc/nginx/vhost.d/default
RUN { \
      echo 'client_max_body_size 100m;'; \
    } > /etc/nginx/conf.d/custom.conf \
