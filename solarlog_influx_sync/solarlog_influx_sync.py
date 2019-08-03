#!/usr/bin/python3
import datetime
from ftplib import FTP
import logging
import pytz
import re

from influxdb import InfluxDBClient

from solarlogcsv.parser import parseline as parse_solarlog_line

def get_last_record_time(influx_client, influx_query):
    result_last_point_query = list(client.query(last_point_query))
    if result_last_point_query:
        return datetime.datetime.fromisoformat(pythonize_iso_timestamp(result_last_point_query[0][0]['time'])).astimezone(pytz.utc)
    else:
        None

def lst_solarlog_files_since(ftp, since_time):
    since_filename = since_time.strftime("min%y%m%d.js")
    prog = re.compile(r'^min\d{6}\.js$')
    files = []
    for filename, properties in ftp.mlsd():
        if prog.match(filename) and filename > since_filename: # Years < 2000 not supported
            files.append(filename)
    return sorted(files)

def solarlog_line_2_influx_measurements(time, inverters_data):
    """ inverters_data is a list of dicts. One dict per inverter """
    influx_points = []
    for i in range(len(inverters_data)):
        influx_point = {
            "measurement": INFLUX_MEASUREMENT_NAME,
            "tags": {
                "inverter": 'WR' + str(i+1)
            },
            "time": time.astimezone(pytz.utc).isoformat().replace('+00:00', 'Z'),
            "fields": {
                "Pac": int(inverters_data[i]['Pac']),
                "Pdc": int(inverters_data[i]['Pdc']),
                "Eday": int(inverters_data[i]['Eday']),
                "Udc": int(inverters_data[i]['Udc'])
            }
        }
        influx_points.append(influx_point)
    return influx_points

def callback_constructor(influx_client, ftp_client, last_time):
    def callback(line):
        time, inverters_data = parse_solarlog_line(line)
        if time > last_time:
            influx_points = solarlog_line_2_influx_measurements(time, inverters_data)
            influx_client.write_points(influx_points)
        else:
            ftp_client.abort()
    return callback

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    SOLARLOG_HOST = os.environ.get('SOLARLOG_HOST', 'solarlog-home3.eu')
    SOLARLOG_USER = os.environ.get('SOLARLOG_USER')
    SOLARLOG_PASSWD = os.environ.get('SOLARLOG_PASSWD')

    INFLUX_HOST = os.environ.get('INFLUX_HOST')
    INFLUX_PORT = int(os.environ.get('INFLUX_PORT')) if  os.environ.get('INFLUX_PORT') else 8086
    INFLUX_DB = os.environ.get('INFLUX_DB')
    INFLUX_MEASUREMENT_NAME = os.environ.get('INFLUX_MEASUREMENT_NAME', solarlog)

    SOLARLOG_ERA_START = int(os.environ.get('SOLARLOG_ERA_START')) \
                            if os.environ.get('SOLARLOG_ERA_START') \
                            else datetime.datetime(2000, 2, 1).timestamp()

    influx = InfluxDBClient(host=INFLUX_HOST,
                            port=INFLUX_PORT)
    influx.create_database(INFLUX_DB)
    influx.switch_database(INFLUX_DB)

    last_point_query = "SELECT * FROM {} ORDER BY time DESC LIMIT 1;".format(INFLUX_MEASUREMENT_NAME)
    result_last_point_query = list(influx.query(last_point_query))
    if result_last_point_query:
        last_time = datetime.datetime.fromisoformat(pythonize_iso_timestamp(result_last_point_query[0][0]['time'])).astimezone(pytz.utc)
    else:
        last_time = datetime.datetime.fromtimestamp(SOLARLOG_ERA_START).astimezone(pytz.utc)

    ftp = FTP(host=SOLARLOG_HOST,
              user=SOLARLOG_USER,
              passwd=SOLARLOG_PASSWD)

    callback = callback_constructor(influx, ftp, last_time)
    if last_time.date() < datetime.datetime.utcnow().date(): # Multiple days to sync
        logging.info("Looking up all files since {} ...".format(last_time))
        listing = lst_solarlog_files_since(ftp, last_time)
        logging.info("Found {} files. Processing ...".format(len(listing)))
        for filename in listing:
            logging.info('Retrieving {}'.format(filename))
            cmd = 'RETR {}'.format(filename)
            ftp.retrlines(cmd, callback=callback)
    else: # Only today to sync
        cmd = 'RETR {}'.format('min_day.js')
        ftp.retrlines(cmd, callback=callback)

    ftp.quit()
