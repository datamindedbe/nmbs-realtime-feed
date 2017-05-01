import json

class Config:
    def __init__(self, path='../config.json'):
        with open(path) as data_file:
            data = json.load(data_file)

        self.bucket = data['bucket']
        self.key_prefix = data['key_prefix']
        self.connection_string = data['connection_string']
        self.feed_url = data['feed_url']
        self.realtime_url = data['realtime_url']
