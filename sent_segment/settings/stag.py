import statsd

MONGO_SERVER = 'mcl1a.southeastasia.cloudapp.azure.com'
MONGO_PORT = 27017

ES_SERVER_IP = '10.10.2.9'
ES_SERVER_PORT = '9200'

CRAWL_DB = 'db_rnd'
MONGO_USER_NAME = 'rnd'
MONGO_PASSWORD = 'delta-pug-rights-eminent-window-skit-somalia-Fairy-128'

STATSD_PREFIX = 'stag.rosetta.'
REMOTE_STATSD_HOST = 'gr1.sg.reverie.co.in'
REMOTE_STATSD_PORT = 8125
statsd_client = statsd.StatsClient(REMOTE_STATSD_HOST, REMOTE_STATSD_PORT, prefix='stag')

"""WSD"""
WSD_MONGODB_HOST = "10.10.2.16"
WSD_MONGODB_HOST_PORT = 27017
WSD_MONGODB_DB_USER_NAME = None
WSD_MONGODB_DB_PASSWORD = None

"""RMT Settings"""
RMT_API_URL = 'http://10.10.1.10/translate/'

"""Reverie Transliteration"""
RTRANS_API_URL = 'http://10.10.1.28:80/transliterate'

"""Aerospike Settings"""
AEROSPIKE_SERVER_IP = '10.210.1.7'
AEROSPIKE_SERVER_PORT = 3000

"""Lokup Server Settings"""
LOOKUP_SERVER_IP = '10.10.2.16'
LOOKUP_SERVER_PORT = 27017
LOOKUP_SERVER_USER_NAME = None
LOOKUP_SERVER_PASSWORD = None
LOOKUP_DB = 'thoth'
LOOKUP_COLLECTION = 'loc_master'

"""LM Servers"""
LM_SERVER_IP = '10.210.1.7'
LM_SERVER_PORT = '8080'

"""Mappings"""
MAPPINGS_SERVER_IP = '10.10.2.16'
MAPPINGS_SERVER_PORT = 27017
MAPPINGS_SERVER_USER_NAME = None
MAPPINGS_SERVER_PASSWORD = None
MAPPINGS_DB = 'entity_default_mappings'
MAPPINGS_COLLECTION = 'default_mappings'
