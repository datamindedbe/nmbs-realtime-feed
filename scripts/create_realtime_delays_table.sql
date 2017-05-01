CREATE TABLE IF NOT EXISTS realtime_updates (
  id                  VARCHAR(255) NOT NULL PRIMARY KEY,
  trip_id             VARCHAR(255) NOT NULL,
  stop_id             VARCHAR(255) NOT NULL,
  trip_start_datetime TIMESTAMP    NOT NULL,
  departure_delay     INT,
  arrival_delay       INT,
  s3_path             VARCHAR(255) NOT NULL,
  creation_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);