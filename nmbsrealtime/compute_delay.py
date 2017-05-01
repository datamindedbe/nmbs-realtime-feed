import os
import sys
import time
import urlparse

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from google.transit import gtfs_realtime_pb2

from config import Config


def persist_delays(connection_string, delays):
    conn = None
    try:
        conn = get_connection(connection_string)
        # create a new cursor
        create_tables(conn)
        new_delays = remove_redundant_delays(conn, delays)
        print("%d new updates" % len(new_delays.keys()))
        if len(new_delays.keys()) > 0:
            insert_delays(conn, new_delays)
    finally:
        if conn is not None:
            conn.close()


def remove_redundant_delays(conn, delays):
    if len(delays.values()) == 0:
        return delays  # no new delays to add
    ids = delays.keys()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """ SELECT * FROM realtime_updates WHERE id IN %(ids)s """
    cur.execute(query, {'ids': tuple(ids)})
    results = cur.fetchall()
    cur.close()
    existing_delays = {get_delay_id(r): r for r in results}
    new_delays = {}
    for key, delay in delays.iteritems():
        # if stop already registered in datbase
        if key in existing_delays:
            current = existing_delays[key]
            # and the file we're reading now is newer than the file in the database
            if current['s3_path'] < delay['s3_path']:
                # and the timings is different
                if current['arrival_delay'] != delay['arrival_delay'] \
                        or current['departure_delay'] != delay['departure_delay']:
                    # then store the change
                    new_delays[key] = delay
        else:
            new_delays[key] = delay
    return new_delays


def get_delay_id(delay):
    return delay['trip_id'] + ':' + delay['stop_id']


def insert_delays(conn, delays):
    cur = conn.cursor()
    delete_query = "DELETE FROM realtime_updates WHERE id IN %(ids)s"
    cur.execute(delete_query, {'ids': tuple(delays.keys())})
    query = """
               INSERT INTO realtime_updates(id, trip_id, stop_id, trip_start_datetime, departure_delay, arrival_delay, s3_path)
               VALUES(
                 %s, %s, %s, to_timestamp(%s, 'yyyymmdd hh24:mi:ss'), %s, %s, %s
               )
           """
    for item in delays.values():
        # execute the INSERT statement
        cur.execute(query, (get_delay_id(item), item['trip_id'], item['stop_id'],
                            item['start_date'] + ' ' + item['start_time'], item['departure_delay'],
                            item['arrival_delay'], item['s3_path']))
        sys.stdout.write('.')
        sys.stdout.flush()
    # commit the changes to the database
    conn.commit()
    print ""
    # close communication with the database
    cur.close()


def create_tables(conn):
    cur = conn.cursor()
    query = open('scripts/create_realtime_delays_table.sql', 'r').read()
    cur.execute(query)
    cur.close()
    conn.commit()


def get_connection(connection_string):
    result = urlparse.urlparse(connection_string)
    conn = psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port = result.port
    )
    # conn = psycopg2.connect(connection_string)
    return conn



def calculate_delays(bucket_name, keys):
    sorted_keys = sorted(keys, key=lambda x: x.last_modified, reverse=False)
    all_delays = {}
    for key in sorted_keys:
        data = boto3.resource('s3').Object(bucket_name, key.key).get()['Body'].read()
        delays = extract_delays(key.key, data)
        all_delays.update(delays)
        print("reading %s. %d updates collected" % (key.key, len(all_delays.keys())))
    return all_delays


def extract_delays(key, data):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)
    results = {}
    try:
        for entity in feed.entity:
            if hasattr(entity, 'trip_update') and hasattr(entity.trip_update, 'stop_time_update'):
                for update in entity.trip_update.stop_time_update:
                    departure_delay = 0
                    arrival_delay = 0
                    if hasattr(update, 'departure') and hasattr(update.departure, 'delay'):
                        departure_delay = update.departure.delay
                    if hasattr(update, 'arrival') and hasattr(update.arrival, 'delay'):
                        arrival_delay = update.arrival.delay
                    delay = {
                        'trip_id': entity.trip_update.trip.trip_id,
                        'start_time': entity.trip_update.trip.start_time,
                        'start_date': entity.trip_update.trip.start_date,
                        'stop_id': update.stop_id,
                        'departure_delay': departure_delay,
                        'arrival_delay': arrival_delay,
                        's3_path': key
                    }
                    results[get_delay_id(delay)] = delay
    except Exception:
        print "Something went wrong processing the realtime feed for %s" % key
        return {}
    return results


def lambda_handler(event, context):
    print event
    print context
    if not 'Records' in event:
        return
    for r in event['Records']:
        if 's3' in r and 'bucket' in r['s3'] and 'name' in r['s3']['bucket'] and 'object' in r['s3'] \
                and 'key' in r['s3']['object']:
            run(r['s3']['bucket']['name'], r['s3']['object']['key'], os.environ['nmbs_connection_string'])


def run(bucket_name, raw_path, connection_string):
    start = time.time()
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    files = bucket.objects.filter(Prefix=raw_path)
    delays = calculate_delays(bucket_name, files)
    persist_delays(connection_string, delays)
    print "total seconds: %d" % (time.time() - start)


def run_local():
    config = Config()
    run(config.bucket, config.key_prefix, config.connection_string)


def catchup(bucket_name, raw_path, connection_string):
    datebucket = '2017/04/28/'
    for i in range(6, 24):
        for j in range(0, 60):
            hourbucket = "%02d%02d" % (i, j)
            run(bucket_name, raw_path + datebucket + hourbucket, connection_string)
