# -*- coding: utf-8 -*-

import codecs
import operator
import re
import string
import time
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import izip_longest

import simplejson
import wordsegment
from nltk import ngrams
from unidecode import unidecode
import enchant

from sent_segment import d_uk, d_us, stop_words, top_5000_words_dict
from common import COMMON_WORDS_THRESHOLD
from sent_segment import d_uk, d_us, stop_words, top_5000_words_dict

from local import COMMON_ABBREVS, COMMON_SHORT_FORMS, SHORT_FORMS_REGEX, TAG_PREFIX, TAG_SUFFIX, \
    COMMON_UNITS

def read_messages(filename):
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.readlines()


def create_corpus(docs):
    doc_corpus = list()
    num_docs = len(docs)
    if not num_docs:
        return doc_corpus
    for text in docs:
        text = text.strip()
        if not text:
            continue
        text = text.replace('},', '}').strip()
        document = simplejson.loads(text)
        doc_corpus.append(document)
    return doc_corpus


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


def compute_similarity(a, b):
    if not a or not b:
        return 0
    a = a.split()
    b = b.split()
    a_tokens = list()
    for t in a:
        if not t.strip():
            # or (is_stop_word(t) and (0 < a.index(t) < (len(a) - 1))):
            continue
        a_tokens.append(t)
    b_tokens = list()
    for t in b:
        if not t.strip():
            # or (is_stop_word(t) and (0 < b.index(t) < (len(b) - 1))):
            continue
        b_tokens.append(t)
    ratios = list()
    for pair in izip_longest(a_tokens, b_tokens):
        t_a = pair[0]
        t_b = pair[1]
        if not t_a or not t_b:
            continue
        ratios.append(SequenceMatcher(None, t_a.strip(), t_b.strip()).ratio())
    if len(ratios):
        score = sum(ratios) / float(max(len(a_tokens), len(b_tokens)))
        return score
    return 0


def levenshtein_distance(a, b):
    if not a or not b:
        return 0
    a = a.split()
    b = b.split()
    a_tokens = list()
    for t in a:
        if not t.strip():
            # or (is_stop_word(t) and (0 < a.index(t) < (len(a) - 1))):
            continue
        a_tokens.append(t)
    b_tokens = list()
    for t in b:
        if not t.strip():
            # or (is_stop_word(t) and (0 < b.index(t) < (len(b) - 1))):
            continue
        b_tokens.append(t)

    distances = list()
    for pair in izip_longest(a_tokens, b_tokens):
        t1 = pair[0]
        t2 = pair[1]
        if not t1 or not t2:
            continue
        oneago = None
        thisrow = range(1, len(t2) + 1) + [0]
        for x in xrange(len(t1)):
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(t2) + [x + 1]
            for y in xrange(len(t2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (t1[x] != t2[y])
                thisrow[y] = min(delcost, addcost, subcost)
        edits = thisrow[len(t2) - 1]
        seq_length = len(t1) + len(t2)
        distances.append(float(seq_length - edits) / float(seq_length))
    if len(distances):
        score = sum(distances) / float(max(len(a_tokens), len(b_tokens)))
        return score
    return 0


def adjust_text_case(text, clean_text):
    case_sensitive_text = ''
    j = 0
    for ch in clean_text:
        if ch.lower() == text[j].lower():
            case_sensitive_text += text[j]
            j += 1
        else:
            case_sensitive_text += ch
    return case_sensitive_text


def spell_correct_candidates(text):
    if is_dict_word(text):
        return text, 1.0
    candidates = dict_word_suggest(text)
    # candidates = sorted([(candidate, compute_similarity(text, candidate)) for candidate in candidates],
    #                     key=itemgetter(1), reverse=True)
    if candidates:
        return candidates[0], compute_similarity(text.lower(), candidates[0].lower())
    return None


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


def is_unit(w):
    if w and w.strip():
        return w.lower() in COMMON_UNITS
    return False


def get_keywords(text, keywords_list):
    tokens = text.lower().split()
    return set(tokens).intersection(set(keywords_list))


def is_dictionary_word(word):
    d_us = enchant.Dict('en_US')
    d_uk = enchant.Dict('en_UK')
    return d_us.check(word) or d_uk.check(word)


def remove_dict_words(word_list):
    return [word for word in word_list if not is_dictionary_word(word)]


def remove_stop_words(terms_list):
    return [term for term in terms_list if term not in stop_words]


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


def get_hindi_ngrams(text, n, keep_punkt=True):
    if keep_punkt:
        text = separate_punkt(text)
    tokens = [t for t in text.split() if t.strip()]
    ngs = list()
    if not tokens:
        return ngs
    for ng in ngrams(tokens, n):
        ngs.append(' '.join(ng))
    return ngs


def separate_punkt(text):
    punkt = [unicode(ch) for ch in list(string.punctuation)]
    punkt += [u'!', u'?', u'|', u':', u';', u"'", u'।']
    txt = ''
    for ch in text:
        if ch in punkt:
            txt = txt + ' ' + ch
        else:
            txt = txt + ch
    return txt


def get_frequent_phrases(phrase_list):
    freq_dict = defaultdict(int)
    for phrase in phrase_list:
        if not phrase:
            continue
        # key = ' '.join(phrase).lower().strip()
        # freq_dict[key] += 1
        freq_dict[phrase] += 1
    return sorted(freq_dict.iteritems(), key=operator.itemgetter(1), reverse=True)