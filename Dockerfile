FROM python:3.7-alpine3.9

COPY . /app

# Git needed by pip for installing git dependencies
RUN apk update && \
    apk add git
RUN pip install /app

CMD [ "python", "/app/solarlog_influx_sync/solarlog_influx_sync.py" ]
