import re
import string
import time
from collections import defaultdict
from operator import itemgetter
from sent_segment.text_utils import cleanup_text, normalize, improve_punctuation
from sent_segment.tagger import remove_tagged_terms
from sent_segment.tagger import replace_account_number, replace_code, replace_date, \
    replace_email, replace_quantity, replace_ordinal
from sent_segment.tagger import replace_percentage, replace_time
from sent_segment.tagger import replace_url, replace_phone_number, replace_money, replace_tzinfo, \
    replace_hashtag, replace_alnum, replace_unicode_strings, replace_html_entities, \
    replace_placeholders, replace_html_tags, replace_number_range, replace_name, \
    replace_version_number, replace_enumeration,replace_unknown_terms
from sent_segment import spacy_utils


def segment_sentences(query, parser=None, pre_tags=None, strip=True, context=None, delim=None):
    """Dirty hack to take care of semgentation issues. If I don't do this
    sentece sentence_segmentation will segment at the '.' I am not proud."""
    temp_tags = list()
    query = ac_num_hack1(query, temp_tags)  # hack to skip sentence_segmentation in case account number
    if not pre_tags:
        pre_tags = defaultdict(list)
    query = replace_common_entities(query, pre_tags, True)
    sentences = spacy_utils.get_sentences(improve_punctuation(query, strip=strip), parser, context=context,
                                              delim=delim)
    # sentences = get_sentences(improve_punctuation(query, strip=strip), context=context, delim=delim)
    if pre_tags:
        sentences = [restore_regex_tags(pre_tags, sent) for sent in sentences]

    """Dirty hack to take care of semgentation issues. If I don't do this
        sentece sentence_segmentation will segment at the '.' I am not proud."""
    sentences = [ac_num_hack2(sent, temp_tags) for sent in sentences]

    return sentences


def ac_num_hack1(query, temp_tags):
    """Dirty hack to take care of semgentation issues. If I don't do this
    sentece sentence_segmentation will segment at the '.' I am not proud."""
    ac_nums = re.findall(r'\b(no\.|num\.)(\s)*(:|-)?(\s)*(\d+|xx+)\b', query, re.IGNORECASE)
    tag = 'ACTEMPTAG'
    for ac in ac_nums:
        ac = ''.join(ac)
        temp_tags.append(ac)
        query = re.sub(ac, tag, query, re.IGNORECASE)
    return query


def ac_num_hack2(query, temp_tags):
    for tag in temp_tags:
        query = re.sub(r'ACTEMPTAG', tag, query, count=1)
    return query


def restore_regex_tags(pre_tags, sent):
    for tag, values in pre_tags.items():
        tag_count = sent.count(tag)
        if not tag_count:
            continue
        for tag_value in values[:tag_count]:
            sent = re.sub(tag, tag_value, sent, count=1)
        pre_tags[tag] = values[tag_count:]
    return sent


def cleanup_and_normalize(text):
    clean_text = cleanup_text(text)
    clean_text = normalize(clean_text)
    return clean_text

def pre_ner_processing(clean_text, tagged_dict, remove_pretagged_terms):
    # if remove_pretagged_terms:
    #     clean_text = remove_tagged_terms(clean_text)
    clean_text = replace_unicode_strings(clean_text, tagged_dict)
    if '@' in clean_text:
        clean_text = replace_email(clean_text, tagged_dict)
    if '.' in clean_text:
        clean_text = replace_url(clean_text, tagged_dict)
    return clean_text

def post_ner_processing(clean_text, tagged_dict, remove_pretagged_terms):
    # if remove_pretagged_terms:
    #     clean_text = remove_tagged_terms(clean_text)
    clean_text = replace_html_entities(clean_text, tagged_dict)
    clean_text = replace_placeholders(clean_text, tagged_dict)
    clean_text = replace_html_tags(clean_text, tagged_dict)
    clean_text = replace_number_range(clean_text, tagged_dict)
    clean_text = replace_percentage(clean_text, tagged_dict)
    clean_text = replace_date(clean_text, tagged_dict)
    clean_text = replace_date(clean_text, tagged_dict)
    clean_text = replace_phone_number(clean_text, tagged_dict)
    clean_text = replace_ordinal(clean_text, tagged_dict)
    clean_text = replace_account_number(clean_text, tagged_dict)
    clean_text = replace_version_number(clean_text, tagged_dict)
    clean_text = replace_enumeration(clean_text, tagged_dict)
    clean_text = replace_money(clean_text, tagged_dict)
    clean_text = replace_hashtag(clean_text, tagged_dict)
    clean_text = replace_code(clean_text, tagged_dict)
    return clean_text


def replace_common_entities(clean_text, tagged_dict, remove_pretagged_terms):
    if remove_pretagged_terms:
        clean_text = remove_tagged_terms(clean_text)
    if '@' in clean_text:
        clean_text = replace_email(clean_text, tagged_dict)
    if '.' in clean_text:
        clean_text = replace_url(clean_text, tagged_dict)

    clean_text = replace_unknown_terms(clean_text, tagged_dict)

    clean_text = replace_unicode_strings(clean_text, tagged_dict)
    clean_text = replace_html_entities(clean_text, tagged_dict)
    clean_text = replace_placeholders(clean_text, tagged_dict)
    clean_text = replace_html_tags(clean_text, tagged_dict)

    clean_text = replace_tzinfo(clean_text, tagged_dict)
    clean_text = replace_date(clean_text, tagged_dict)
    clean_text = replace_time(clean_text, tagged_dict)
    clean_text = replace_percentage(clean_text, tagged_dict)
    clean_text = replace_quantity(clean_text, tagged_dict)

    clean_text = replace_number_range(clean_text, tagged_dict)
    clean_text = replace_name(clean_text, tagged_dict)

    clean_text = replace_ordinal(clean_text, tagged_dict)
    clean_text = replace_money(clean_text, tagged_dict)

    #clean_text = replace_alnum(clean_text, tagged_dict)

    clean_text = replace_version_number(clean_text, tagged_dict)
    clean_text = replace_enumeration(clean_text, tagged_dict)

    clean_text = replace_phone_number(clean_text, tagged_dict)

    clean_text = replace_account_number(clean_text, tagged_dict)
    clean_text = replace_hashtag(clean_text, tagged_dict)
    clean_text = replace_code(clean_text, tagged_dict)
    clean_text = replace_alnum(clean_text, tagged_dict)
    #clean_text = replace_phrases(clean_text, tagged_dict)

    return clean_text
