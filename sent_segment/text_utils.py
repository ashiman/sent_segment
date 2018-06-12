# -*- coding: utf-8 -*-

import codecs
import operator
import re
import string
import time
import wordsegment
from unidecode import unidecode
from sent_segment import d_uk, d_us, stop_words, top_5000_words_dict
from sent_segment.common import COMMON_WORDS_THRESHOLD
from sent_segment import d_uk, d_us, stop_words, top_5000_words_dict

from sent_segment.local import COMMON_ABBREVS, COMMON_SHORT_FORMS, SHORT_FORMS_REGEX, TAG_PREFIX, TAG_SUFFIX, \
    COMMON_UNITS


def cleanup_text(text):
    text = text.strip()
    if not text:
        return None
    text = unicode(' '.join([t.strip() for t in text.split() if t.strip()]))
    text = text.replace('\n', ' ').replace('.!', '!').replace('.?', '?').replace(u'’', "'")
    text = ' '.join([t.strip() for t in text.replace('&', ' and ').replace('@', ' at ').split() if t.strip()])
    text = re.sub(TAG_SUFFIX + TAG_PREFIX, TAG_SUFFIX + ' ' + TAG_PREFIX, text)
    text = re.sub(ur'\s+([.!?:,\)])', ur'\1', text)
    text = unidecode(text)
    return text


def improve_punctuation(text, strip=True):
    text = re.sub(ur'(no\.|num\.)(\s)(\d+|xx+)\b', '\1\3', text, re.IGNORECASE)
    text = re.sub(ur'([.,!?;:%])([a-zA-Z]+)', r'\1 \2', text)
    text = re.sub(ur'\b(\w+)(\([\w\s]{2,}\))', ur'\1 \2', text)
    if strip:
        text = re.sub(ur'(\w+|<\w+>)\s+([.,!?;:%])', r'\1\2', text)
        text = ' '.join(text.split())
    return text


# normalizes common abbreviation(govt, apr, bglr) into words(government, april, bangalore)
def normalize(text):
    text = text.replace(u'’', "'")
    tokens = text.split()
    for idx, term in enumerate(tokens):
        term = term.strip()
        if term.lower() in COMMON_ABBREVS.keys():
            tokens[idx] = COMMON_ABBREVS.get(term.lower())
        # elif term.lower() in COMMON_SHORT_FORMS:
        #     tokens[idx] = COMMON_SHORT_FORMS.get(term.lower())
    text = unicode(' '.join(tokens))
    for pattern, value in SHORT_FORMS_REGEX.iteritems():  # strings like acc into account
        text = re.sub(pattern, value, text, flags=re.IGNORECASE)
    return text


def segment_text(text):
    segments = wordsegment.segment(text)
    return segments


def is_dict_word(w):
    try:
        if d_us.check(w) or d_uk.check(w):
            return True
        return False
    except TypeError:
        return False


def dict_word_suggest(w):
    if not w:
        return None
    return d_us.suggest(w)

def is_stop_word(word):
    t0 = time.time()
    status = word in stop_words
    t1 = time.time()
    return status


def is_common_word(word, threshold=COMMON_WORDS_THRESHOLD):
    idx = top_5000_words_dict.get(word, None)
    if not idx or idx > threshold:
        return False
    return True


def is_common_phrase(phrase, threshold=COMMON_WORDS_THRESHOLD):
    t0 = time.time()
    tokens = [t.strip() for t in phrase.split()]
    tokens_len = len(''.join(tokens))
    common_words = [t for t in tokens if is_stop_word(t) or is_common_word(t.lower(), threshold)]
    common_words_len = len(''.join(common_words))
    len_ratio = float(common_words_len) / float(tokens_len)
    num_ratio = float(len(common_words)) / float(len(tokens))
    if len_ratio < 0.75 or num_ratio < 0.75:
        return False
    t1 = time.time()
    return True

