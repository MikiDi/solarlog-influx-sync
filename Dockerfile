FROM python:3.7-stretch

COPY . /app

RUN pip install /app

CMD [ "python", "/app/solarlog_influx_sync/solarlog_influx_sync.py" ]
