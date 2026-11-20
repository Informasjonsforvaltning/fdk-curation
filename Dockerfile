FROM nginx:1.31.9-alpine-slim

ENV CURATION_VERSION=unknown

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY high-value-dataset-types.csv /usr/share/nginx/html/high-value-dataset-types.csv

USER 101
