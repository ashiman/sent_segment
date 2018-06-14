# Settings common across deployment environments.
import os
# Define log directory and file.
# Set formatter to logstash format.
# Set level to INFO
# LOGS_DIR = '/var/log/data_pipeline/'
# logger = logging.getLogger('rosetta')
# hdlr = logging.FileHandler(os.path.join(LOGS_DIR, 'rosetta_apis.log'))


# <LEGACY SETTINGS>
# These are some legacy settings related to fetching crawled data from
# DataWeave. They had exposed an API using which we got the data.
# Not relevant anymore
# RETAIL_MISSING_DATA_FILE = os.path.join(LOGS_DIR, 'dw_missing_data')
# RETAIL_URLH_FILE = os.path.join(LOGS_DIR, 'dw_retail_urlh')

# DW_API_KEY = 'c74dc287a17f9410182de76184559e08'
DW_API_KEY = '4453b9e9738ca0f67922b2e20e2677ea'
DW_RETAIL_CATALOG_API = 'http://rosetta.dataweave.in/v1/priceintelligence_api/fetchCatalogBundles/'
DW_RETAIL_HTML_PAGE_API = 'http://cache.dataweave.com/html_archives/'
DW_JOBS_API = 'http://rosetta.dataweave.in/v1/priceintelligence_api/fetchJobs/'
DEFAULT_PER_PAGE = 500
# <LEGACY SETTINGS>

# Knowledgebase Related Settings
# Settings related to creation of knowledgebase for different domains.
# Data is stored in MongoDB and Elastic using this schemata.
RETAIL_REQUIRED_FIELDS = [u'sub_category', u'meta', u'features', u'category', u'title', u'source', u'stock',
                          u'description', u'specifications', u'brand', u'others', u'product_type', u'url',
                          u'urlh']
RETAIL_ENTITIES = [u'sub_category', u'category', u'product_type', u'brand']
RETAIL_HIERARCHY = {
    'brand': ['source', 'product_type', 'sub_category', 'category'],
    'product_type': ['source', 'brand', 'sub_category', 'category'],
    'sub_category': ['source', 'brand', 'category'],
    'category': ['source', 'brand']
}

RETAIL_COLLECTION = 'dw_retail'
RETAIL_ENTITIES_COLLECTION = 'dw_retail_entities'
RETAIL_SENTENCE_FIELDS = ['features', 'title', 'specifications', 'description', 'meta']


JOBS_ENTITIES = [u'category', u'employer', u'city', u'industry', u'salary']
JOBS_HIERARCHY = {
    'category': ['salary', 'employer', 'city', 'industry'],
    'employer': ['salary', 'city', 'category'],
    'industry': ['employer', 'city', 'salary'],
    'salary': ['category', 'city', 'industry'],
    'city': ['category', 'industry', 'salary']
}

JOBS_COLLECTION = 'dw_jobs'
JOBS_ENTITIES_COLLECTION = 'dw_jobs_entities'
JOBS_SENTENCE_FIELDS = ['salary', 'title', 'description', 'address', 'contact']


ENTERTAINMENT_ENTITIES = ['genre', 'actor', 'director', 'writer', 'title', 'source']
ENTERTAINMENT_HIERARCHY = {
    'source': ['genre', 'actor', 'director', 'writer'],
    'genre': ['director', 'actor', 'writer', 'source'],
    'actor': ['genre', 'director', 'writer'],
    'writer': ['genre', 'directror', 'actor'],
    'director': ['genre', 'writer', 'actro'],
    'title': ['source']
}

ENTERTAINMENT_COLLECTION = 'entertainment'
ENTERTAINMENT_ENTITIES_COLLECTION = 'entertainment_entities'
ENTERTAINMENT_SENTENCE_FIELDS = ['plot', 'title']

# Names of indexes in Elastic
ES_ENTITY_INDEX_NER = 'named_entities'
ES_ENTITY_INDEX = 'domain_entities'
ES_DOMAIN_TEXT_INDEX = 'domain_text'
NGRAMS_INDEX = 'retail_ngrams'
HINDI_NGRAMS_INDEX = 'hindi_ngrams'
TERM_COOCCURRENCE_GRAPH_INDEX = 'term_cooccurrence_graph'

# Names of collections in MongoDB
TEXT_CORPUS_DB = 'text_corpora'
HINDI_TEXT_COLLECTION = 'hi_text'
EN_HI_PARALLEL_CORPUS_COLLECTION = 'he_parallel_corpus'
SPELLING_ERRORS_COLLECTION = 'spelling_errors'

PER_PAGE = 1000

# Thresholds used in entity tagging
SIMILARITY_THRESHOLD = 0.9
SCORE_THRESHOLD = 1000.0
LEEWAY_TAGS = ['category', 'sub_category', 'product_type', 'commontechnicalterm']

"""Azure related settings"""
AZURE_CLIENT_ID = '4660756e-654c-4d7a-b101-a8b1e51bae58'
AZURE_CLIENT_SECRET = 'AOFZDa1gVQ8UlMtNVxcB4TYxL5CMlpm1g4vMP6IOr0Y='

"""Google Cloud API settings"""
GOOGLE_CLOUD_API_KEY = 'AIzaSyBRT1tm5Qx64MuQGpP5Z7p3algSKpsxKWs'

"""Managed Translation related settings"""
TRANSLATION_ENGINES = ['google++', 'google', 'reverie']

LANGUAGE_CODES_MAPPING = {'hindi': 'hi',
                          'punjabi': 'pa',
                          'gujarati': 'gu',
                          'bengali': 'bn',
                          'tamil': 'ta',
                          'telugu': 'te',
                          'kannada': 'kn',
                          'malayalam': 'ml',
                          'urdu': 'ur',
                          'marathi': 'mr',
                          'oriya': 'or',
                          'odia': 'or',
                          'english': 'en',
                          'assamese': 'as'
                          }
LANGUAGE_CODE_TO_NAME_MAPPING = {'hi': 'hindi',
                                 'pa': 'punjabi',
                                 'gu': 'gujarati',
                                 'bn': 'bengali',
                                 'ta': 'tamil',
                                 'te': 'telugu',
                                 'kn': 'kannada',
                                 'ml': 'malayalam',
                                 'ur': 'urdu',
                                 'mr': 'marathi',
                                 'or': 'odia',
                                 'en': 'english',
                                 'as': 'assamese'
                                 }

SUPPORTED_LANGUAGES = ['hi', 'pa', 'gu', 'bn', 'ta', 'te', 'kn', 'ml', 'ur', 'mr', 'or', 'en']

BING_LANGUAGES = ['hi', 'ur', 'en']
REVERIE_LANGUAGES = ['hi']

GOOGLE_INPUT_URL_PREFIX = """https://inputtools.google.com/request?text=%s&itc="""
GOOGLE_INPUT_URL_SUFFIX = """-t-i0-und&num=13&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"""
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin': 'http://www.google.co.in',
    'Referer': 'http://www.google.co.in/inputtools/try/',
    'Save-Data': 'on',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

MODELS_DIR = "./models"

"""Classifer related settings"""
SENTENCE_MODELS_FILE = os.path.join(MODELS_DIR, 'classification/sentence_model.bin')
TERM_MODEL_FILE = os.path.join(MODELS_DIR, 'classification/terms_model.bin')
CONTEXT_MODEL_FILE = os.path.join(MODELS_DIR, 'classification/context_model.bin')


"""WSD"""
ADV = "ADVERB"
ADJ = "ADJECTIVE"
NOUN = "NOUN"
VERB = "VERB"

WORD_EMBEDDINGS_MODELS_DIR = os.path.join(MODELS_DIR, 'word_embeddings')
WORD2VEC_MODEL_FILE = os.path.join(MODELS_DIR, 'word_embeddings/GoogleNews-vectors-negative300.bin')
WSD_MONGODB_DB_NAME = "wordnet_for_wsd"
WSD_MONGODB_INDOWORDNET_COLLECTION = "indowordnet_english_hindi"
WSD_MONGODB_AAMBOLI_HINDIERA_MIXED_COLLECTION = "aamboli_hindiera_wn"

"""Language Detection related settings"""
LANGUAGE_DETECTION_MODEL_FILE = os.path.join(MODELS_DIR, 'lang_detect/gdelt_lang_detect_model.bin')

"""Language related settings"""
COMMON_WORDS_THRESHOLD = 500

"""Caching settings
    - 0, for no caching
    - 1, for caching only entities
    - 2, for caching all queries """
CACHING = 0

"""Names Classification Related Settings"""
NAMES_CLASSIFICATION_MODEL_FILE = os.path.join(MODELS_DIR, 'classification/names_model.hdf5')

"""NWP Related Settings"""
PROGRESSIVE_PREDICTION_MODEL = os.path.join(MODELS_DIR, 'nwp/hi_gdeltv2_char.hdf5')

"""N-gram LM related settings"""
NGRAM_LMS_MODELS_DIR = os.path.join(MODELS_DIR, 'language_models')
NGRAM_CHAR_LM_MODEL_FILES = {'hindi': 'hi-gdeltv2-kneserney-5-char-kenlm.binary',
                             'kannada': 'kn-gdeltv2-kneserney-5-char-kenlm.binary'}
NGRAM_WORD_LM_MODEL_FILES = {'hindi': 'hi-gdeltv2-kneserney-5-kenlm.binary',
                             'kannada': 'kn-gdeltv2-kneserney-5-kenlm.binary'}

BANKING_DOMAIN = 5
