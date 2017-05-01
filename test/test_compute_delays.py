import json
import os

import psycopg2
import pytest
import testing.postgresql

from nmbsrealtime import compute_delay


@pytest.fixture
def sample_event():
    with open('test/test_event.json') as data_file:
        return json.load(data_file)


def test_trigger_lambda_handler_executes_correctly(sample_event):
    with testing.postgresql.Postgresql() as postgresql:
        os.environ['nmbs_connection_string'] = postgresql.url()
        compute_delay.lambda_handler(sample_event, None)
