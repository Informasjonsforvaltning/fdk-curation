FROM nginxinc/nginx-unprivileged:1.28-alpine

ENV CURATION_VERSION=unknown

RUN sed -i 's/^worker_processes.*/worker_processes 1;/' /etc/nginx/nginx.conf

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY high-value-dataset-types.csv /usr/share/nginx/html/high-value-dataset-types.csv
