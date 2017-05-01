# nmbs-realtime
nmbs-realtime is a Python tool to parse the realtime stream of NMBS. To get access to NMBS open data, you need to fill out this form here: http://www.belgianrail.be/nl/klantendienst/infodiensten-reistools/public-data.aspx


## Retrieve data
`store_in_s3.py` retrieves the current NMBS realtime feed and stores it in S3. It can be used with AWS Lambda by calling `lambda_handler` and setting the following environment variables:

- `nmbs_realtime_feed_url`: the url of the NMBS feed
- `bucket`: the S3 bucket where you want to store the file
- `key_prefix`: the path in which files are stored.

It can also be called manually by moving `config.template.json` to `config.json` and configuring this file.

## Compute delays
Once data is retrieved, delays need to be calculated. This script stores delays in a database, and if new delays arrives, it checks which ones it should keep. For every `trip_id, stop_id` combination, we only keep the last delay information. It can either run on Lambda, by setting a trigger for a new file created in S3, or local. If running on lambda, the following environment variable is needed:

- `connection_string`: The connection string to the database to store the delays.

The other parameters (bucket name and key name) it will get from the lambda event.  Running manual is the same as above. The settings should be in `config.json`.

 ## Deploy using Lambda
 Lambda is a convenient service for running python scripts without having to host the infrastructure. I've added the deployment scripts to lambda in the `scripts/` folder. However, there were a few issues:

 - I had to compile the `psycopg2` library in an AWS linux instance because compiled locally on a mac, it didn't run in the Lambda environment.. I committed it in `libs/`.
 - I added a `__init__.py file in `deploy/google` because otherwise it wouldn't import from `google.transit`

## Stability
This is Alpha software with no warranties. I added a smoke test but should add more tests in the future.