FROM python:3.7-alpine3.9

COPY . /app

RUN apk update && \
    apk add git
RUN pip install /app

CMD [ "python", "/app/solarlog_influx_sync/solarlog_influx_sync.py" ]
