# -*- coding: utf-8 -*-

import re
import string

from sent_segment.entity_tagging import COMMON_HONORIFICS, COMMON_UNITS
from sent_segment.text_utils import is_dict_word, segment_text, is_common_phrase
from sent_segment.local import TAG_SUFFIX, TAG_PREFIX
from sent_segment.misc_utils import multikeysort, MyHTMLParser


def replace_alnum(text, tagged_dict):
    tag_name = TAG_PREFIX + r'ALNUM' + TAG_SUFFIX
    pattern = re.compile(r'\b((?=[A-Za-z\/-]{0,19}\d)[A-Za-z0-9-,\/]{4,20})\b')

    #pattern = re.compile(ur'\b(([A-Z/ -]{0,19}\d)[A-Z0-9/ -,]{4,20})\b')
    alnums = pattern.findall(text)
    for alnum in alnums:
        value = ''.join(alnum).strip()
        if is_tag(value):
            continue
        tagged_dict[tag_name].append(value)
        text = re.sub(value, tag_name, text, count=1)
    return text


def replace_quantity(text, tagged_dict):
    tag_name = TAG_PREFIX + r'QUANTITY' + TAG_SUFFIX
    unit = '|'.join(COMMON_UNITS)
    unit = r'(' + unit + r')(s?)\b'
    quantity = r'\b(((\d+[\.,]?\d*)(\s*[Xx\-~(to)]\s*\d+[\.,]?\d*)*\s*)' + unit + r')\b'
    pattern = re.compile(quantity, re.IGNORECASE)
    quantities = pattern.findall(text)
    for qty in quantities:
        if not len(qty):
            continue
        value = ''.join(qty[0]).strip()
        tagged_dict[tag_name].append(value)
        text = re.sub(value, tag_name, text, count=1)
    return text


def replace_name(text, tagged_dict):
    tag_name = TAG_PREFIX + r'PERSON' + TAG_SUFFIX
    honorific = '|'.join(COMMON_HONORIFICS)
    honorific = r'\b(' + honorific + r')(\.)?(\s)*'
    name = honorific + r'([A-Z][a-z]+\s?)([A-Z][a-z]+\s)?\b([A-Z][a-z]+)?\b'
    pattern = re.compile(name)
    names = pattern.findall(text)
    for name in names:
        value = ''.join(name).strip()
        tagged_dict[tag_name].append(value)
        text = re.sub(value, tag_name, text, count=1)
    return text


def replace_money(text, tagged_dict):
    tag_name = TAG_PREFIX + r'AMOUNT' + TAG_SUFFIX
    re_1 = re.compile(r'(₹|\brs|usd|rupees|inr)(\.)?(\s)?(\d+|xx+)(,\d+|,xx+)*(\.\d+|xx+)?\b', re.IGNORECASE)
    if re.search(re_1, text):
        amounts = re.findall(re_1, text)
        for amt in amounts:
            tagged_dict[tag_name].append(''.join(amt).strip())
        return re.sub(re_1, tag_name, text)
    re_2 = re.compile(r'\b(\d+|xx+)(\s)?(lakhs|lakh|lacs|lac|crores|crore|cr)\b', re.IGNORECASE)
    if re.search(re_2, text):
        amounts = re.findall(re_2, text)
        for amt in amounts:
            tagged_dict[tag_name].append(''.join(amt).strip())
        return re.sub(re_2, tag_name, text)
    return text


def replace_time(text, tagged_dict):
    original_tokens = text.split()
    text = re.sub("a.m.", "am", text, flags=re.IGNORECASE)
    text = re.sub("p.m.", "pm", text, flags=re.IGNORECASE)

    tag_name = TAG_PREFIX + r'TIME' + TAG_SUFFIX
    dts = re.findall(r'\b(\d{1,2}\s?:\s?\d{2}\s?)(:\s?\d{2})?(\s)*(am|pm|a.m.|p.m.|oclock|o\'clock)?\b',
                     text, flags=re.IGNORECASE)
    for dt in dts:
        dt_val = ''.join(dt).strip()
        tagged_dict[tag_name].append(dt_val)
        text = re.sub(dt_val, tag_name, text, flags=re.IGNORECASE, count=1)
    dts = re.findall(r'\b(\d{1,2})(\s)*(am|pm|a.m.|p.m.|oclock|o\'clock)\b', text, flags=re.IGNORECASE)
    for dt in dts:
        dt_val = ''.join(dt).strip()
        tagged_dict[tag_name].append(dt_val)
        text = re.sub(dt_val, tag_name, text, flags=re.IGNORECASE, count=1)
    if tag_name in tagged_dict:
        tagged_dict[tag_name] = reoroder_tag_list(original_tokens, tagged_dict[tag_name])
    return text


def replace_tzinfo(text, tagged_dict):
    tag_name = TAG_PREFIX + r'TIMEZONE' + TAG_SUFFIX
    tzs = re.findall(r'\b(gmt)(\+)?\s?(\d{1,2}|x+)(:)?(\d{1,2}|x+)?\b', text, flags=re.IGNORECASE)
    for tz in tzs:
        tz_val = ''.join(tz).strip()
        tagged_dict[tag_name].append(tz_val)
    return re.sub(r'\b(gmt)(\+)?\s?(\d{1,2}|x+)(:)?(\d{1,2}|x+)?\b', tag_name, text, flags=re.IGNORECASE)


def replace_ordinal(text, tagged_dict):
    tag_name = TAG_PREFIX + r'ORDINAL' + TAG_SUFFIX
    ordinals = re.findall(r'\b(\d+)(nd|th|rd|st)\b', text, flags=re.IGNORECASE)
    for ordinal in ordinals:
        tagged_dict[tag_name].append(''.join(ordinal).strip())
    return re.sub(r'\b(\d+)(nd|th|rd|st)\b', tag_name, text, flags=re.IGNORECASE)


def replace_cardinal(text, tagged_dict):
    original_tokens = text.split()

    tag_name = TAG_PREFIX + r'CARDINAL' + TAG_SUFFIX
    nums = re.findall(r'(\d+\.?\d*)(\s+)(thousand|million|billion|trillion|lac|lakh|crore)\b',
                      text, re.IGNORECASE)
    for n in nums:
        tagged_dict[tag_name].append(''.join(n).strip())
    text = re.sub(r'(\d+\.?\d*)(\s+)(thousand|million|billion|trillion|lac|lakh|crore)\b',
                  tag_name, text, flags=re.IGNORECASE)

    biggies = ['thousand', 'million', 'billion', 'trillion', 'lac', 'lakh', 'crore']
    num_regex = r'\b(one|eleven|two|twelve|three|thirteen|four|fourteen|five|fifteen|' \
                r'six|sixteen|seven|seventeen|eight|eighteen|nine|nineteen|ten|twenty|thirty|' \
                r'forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|' \
                r'trillion|lac|lakh|crore)\b'
    tokens = re.findall(r"[\w']+|[.,!?;]", text)
    numbers = re.findall(num_regex, text, re.IGNORECASE)
    num_groups = list()
    idx = 0
    while idx < len(tokens):
        group = list()
        for token in tokens[idx:]:
            if token.lower() in biggies:
                if tokens.index(token) != 0:
                    if re.match(r'\d+\.?\d*', tokens[tokens.index(token) - 1]):
                        idx += 2
                        break
            if token in numbers:
                group.append(token)
                idx += 1
                if idx == len(tokens):
                    num_groups.append(' '.join(group))
            elif token.lower() == 'and' and len(group):
                group.append(token)
                idx += 1
                if idx == len(tokens):
                    num_groups.append(' '.join(group))
            else:
                if group:
                    num_groups.append(' '.join(group))
                    idx += 1
                    break
                idx += 1
    for group in num_groups:
        group_re = r'\b' + group + r'\b'
        tagged_dict[tag_name].append(group.strip())
        text = re.sub(group_re, tag_name, text, count=1, flags=re.IGNORECASE)

    if tag_name in tagged_dict:
        tagged_dict[tag_name] = reoroder_tag_list(original_tokens, tagged_dict[tag_name])

    return text


def replace_date(text, tagged_dict, tag_name=None):
    original_tokens = text.split()
    if not tag_name:
        tag_name = TAG_PREFIX + r'DATE' + TAG_SUFFIX
    dates = re.findall(r'\b(\d{1,2}\s*[/\-]\s*\d{1,2}\s*[/\-]\s*\d{2,4})\b',
                       text, flags=re.IGNORECASE)
    for dt in dates:
        tagged_dict[tag_name].append(''.join(dt).strip())
    text = re.sub(r'\b(\d{1,2}\s*[/\-]\s*\d{1,2}\s*[/\-]\s*\d{2,4})\b', tag_name,
                  text, flags=re.IGNORECASE)

    dates = re.findall(r'\b(\d{1,2}|xx+)(nd|th|rd|st)?(\s)?(january|jan|february|feb|march|mar|'
                       r'april|apr|may|june|jun|july|jul|august|aug|september|sept|sep|october|'
                       r'oct|november|nov|december|dec)(\s)?(,)?(\s)?(\d{2,4}|x+)?\b',
                       text, flags=re.IGNORECASE)

    for dt in dates:
        dt_val = ''.join(dt).strip()
        tagged_dict[tag_name].append(dt_val)
        text = re.sub(dt_val, tag_name, text, flags=re.IGNORECASE)

    dates = re.findall(r'\b(january|jan|february|feb|march|mar|april|apr|may|june|jun|'
                       r'july|jul|august|aug|september|sept|sep|october|oct|november|nov'
                       r'december|dec)(\s)?(\d{1,2}|xx+)(nd|th|rd|st)?(\s)?(\d{,4}|x+)?\b',
                       text, flags=re.IGNORECASE)
    for dt in dates:
        dt_val = ''.join(dt).strip()
        tagged_dict[tag_name].append(''.join(dt).strip())
        text = re.sub(dt_val, tag_name, text, flags=re.IGNORECASE)

    if tag_name in tagged_dict:
        tagged_dict[tag_name] = reoroder_tag_list(original_tokens, tagged_dict[tag_name])

    return text


def replace_phone_number(text, tagged_dict):
    tag_name = TAG_PREFIX + r'PHONENUMBER' + TAG_SUFFIX
    phones = re.findall(r'\b(ph:|mobile|mobile no.|call on|calling on|calling|call us|'
                        r'call [a-z]* @|sms [a-z]*|contact|call)\s\+?(\d+|xx+)\b',
                        text, flags=re.IGNORECASE)
    for ph in phones:
        ph_val = ''.join(ph[1:])
        tagged_dict[tag_name].append(ph_val)
        text = re.sub(ph_val, tag_name, text)
    # return re.sub(ur'(ph:|mobile|mobile no.|call on|calling on|calling|call us|'
    #               ur'call [a-z]* @|sms [a-z]*|contact|call)\s\+?(\d+|xx+)',
    #               r'\1 ' + tag_name + ' ', text, flags=re.IGNORECASE)
    return text


def replace_url(text, tagged_dict, tag_name=None):
    original_tokens = text.split()

    tag_name = TAG_PREFIX + r'URL' + TAG_SUFFIX
    url_regex = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|"\
                      r'edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|'\
                      r'post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|'\
                      r'aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|'\
                      r'cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|'\
                      r'do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|'\
                      r'gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|'\
                      r'io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|'\
                      r'li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|'\
                      r'mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|'\
                      r'pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|'\
                      r'sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|'\
                      r'tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|'\
                      r'vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)'\
                      r'[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|'\
                      r"""[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.]"""\
                      r"(?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|"\
                      r"name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|"\
                      r"aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|"\
                      r"cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|"\
                      r"eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|"\
                      r"gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|"\
                      r"jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|"\
                      r"md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|"\
                      r"ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|"\
                      r"rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|"\
                      r"sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|"\
                      r"vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))\b"
    urls = re.findall(url_regex, text)
    for url in urls:
        url_val = ''.join(url).strip()
        tagged_dict[tag_name].append(url_val)
        #text = re.sub(url_val, tag_name, text, re.IGNORECASE)

    text = re.sub(url_regex, tag_name, text, flags=re.IGNORECASE)

    urls = re.findall(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-zA-Z0-9.\-]+[.][a-zA-Z]{2,4}/)'
                      r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
                      r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{}'
                      r';:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))', text)
    for url in urls:
        url_val = ''.join(url).strip()
        tagged_dict[tag_name].append(url_val)
        text = re.sub(url_val, tag_name, text, re.IGNORECASE)

    urls = re.findall(r'\b([\w]+\s?\.co\s?\.in|[\w]+\s?\.com)\b', text)
    for url in urls:
        url_val = ''.join(url).strip()
        tagged_dict[tag_name].append(url_val)
        text = re.sub(url_val, tag_name, text, re.IGNORECASE)

    if tag_name in tagged_dict:
        tagged_dict[tag_name] = reoroder_tag_list(original_tokens, tagged_dict[tag_name])

    return text


def replace_email(text, tagged_dict, tag_name=None):
    if not tag_name:
        tag_name = TAG_PREFIX + r'EMAILID' + TAG_SUFFIX
    emails = re.findall(r'\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b', text, flags=re.IGNORECASE)
    for email in emails:
        tagged_dict[tag_name].append(''.join(email).strip())
    return re.sub(r'\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b', tag_name,
                  text, flags=re.IGNORECASE)


def replace_hashtag(text, tagged_dict):
    tag_name = TAG_PREFIX + r'HASHTAG' + TAG_SUFFIX
    hashtags = re.findall('\b(#[a-zA-Z0-9]+)\b', text, flags=re.IGNORECASE)
    for ht in hashtags:
        ht = ''.join(ht)
        tagged_dict[tag_name].append(ht)
        text = re.sub(ht, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_account_number(text, tagged_dict):
    tag_name = TAG_PREFIX + r'ACCOUNTNUMBER' + TAG_SUFFIX
    ac_nums = re.findall(r'\b(account|acc|a/c|ac)(\s)*(number|no\.?|num\.?)(\s)*(:|-)?(\s)*(\d+|xx+)\b',
                         text, flags=re.IGNORECASE)
    for ac in ac_nums:
        ac_val = ac[-1].strip()
        tagged_dict[tag_name].append(ac_val)
        text = re.sub(ac_val, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_code(text, tagged_dict):
    original_tokens = text.split()
    tag_name = TAG_PREFIX + r'CODE' + TAG_SUFFIX
    codes = re.findall(r'\b(code|cpn|coupon code|coupon)(:)?(\s)?(\w+)\b', text)
    for code in codes:
        code = code[-1]
        tagged_dict[tag_name].append(code)
        text = re.sub(code, tag_name, text, flags=re.IGNORECASE, count=1)
    codes = re.findall(r'\b(xx+\w+x*|\w+xx+\w+)\b',
                       text, flags=re.IGNORECASE)
    for code in codes:
        code = ''.join(code)
        tagged_dict[tag_name].append(code)
        text = re.sub(code, tag_name, text, flags=re.IGNORECASE, count=1)

    if tag_name in tagged_dict:
        tagged_dict[tag_name] = reoroder_tag_list(original_tokens, tagged_dict[tag_name])

    return text


def replace_unicode_strings(text, tagged_dict):
    tag_name = TAG_PREFIX + r'UNICODESTRING' + TAG_SUFFIX
    unicode_strings = re.findall(r'\b(U\+[0-9a-fA-F]{4,})\b', text, flags=re.IGNORECASE)
    for uni_str in unicode_strings:
        value = ''.join(uni_str).strip()
        tagged_dict[tag_name].append(value)
    return re.sub(r'\b(U\+[0-9a-fA-F]{4,})\b', tag_name, text, flags=re.IGNORECASE)


def replace_placeholders(text, tagged_dict):
    tag_name = TAG_PREFIX + r'PLACEHOLDER' + TAG_SUFFIX
    placeholders = re.findall(r'((%\d+\$[a-z]+\s?,?\s*)+\b)', text, flags=re.IGNORECASE)
    for ph in placeholders:
        if not len(ph):
            continue
        value = ''.join(ph[0]).strip()
        tagged_dict[tag_name].append(value)
    return re.sub(r'((%\d+\$[a-z]+\s?,?\s*)+\b)', tag_name, text, flags=re.IGNORECASE, count=1)


def replace_html_entities(text, tagged_dict):
    tag_name = TAG_PREFIX + r'HTMLENTITY' + TAG_SUFFIX
    html_entities = re.findall(r'(&[a-zA-Z]+;)', text, flags=re.IGNORECASE)
    for ent in html_entities:
        value = ''.join(ent).strip()
        tagged_dict[tag_name].append(value)
        text = re.sub(value, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_html_tags(text, tagged_dict):
    html_parser = MyHTMLParser()
    html_parser.feed(text)
    tags = html_parser.tag_list
    tag_name = TAG_PREFIX + r'HTMLTAG' + TAG_SUFFIX
    for tag in tags:
        tagged_dict[tag_name].append(tag)
        text = re.sub(tag, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_percentage(text, tagged_dict):
    tag_name = TAG_PREFIX + r'PERCENT' + TAG_SUFFIX
    percentages = re.findall(r'\b(\d+\.?\d*\s*%|xx+\.?xx*\s*%)', text, flags=re.IGNORECASE)
    for perc in percentages:
        tagged_dict[tag_name].append(''.join(perc).strip())
    return re.sub(r'\b(\d+\.?\d*\s*%|xx+\.?xx*\s*%)', tag_name, text, flags=re.IGNORECASE)


def replace_number(text, tagged_dict, tag_name=None):
    if not tag_name:
        tag_name = TAG_PREFIX + r'NUMBER' + TAG_SUFFIX
    numbers = re.findall(r'\b(\d+|xx+)(\.)(\d+|xx+)\b|\b(\d+|xx+)\b',
                         text)
    for num in numbers:
        num = ''.join(num)
        tagged_dict[tag_name].append(num)
        text = re.sub(num, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_number_range(text, tagged_dict):
    tag_name = TAG_PREFIX + r'NUMBER' + TAG_SUFFIX
    ranges = re.findall(r'((\d+[\.,]?\d*)(\s*[Xx\-~]\s*\d+[\.,]?\d*)+)', text)
    for r in ranges:
        if not len(r):
            continue
        val = ''.join(r[0])
        tagged_dict[tag_name].append(val)
        text = re.sub(val, tag_name, text, flags=re.IGNORECASE, count=1)
    return text


def replace_version_number(text, tagged_dict):
    tag_name = TAG_PREFIX + r'NUMBER' + TAG_SUFFIX
    version_nums = re.findall(r'\b((\d+[\.,])+\d+)\b', text)
    for ver in version_nums:
        if not len(ver):
            continue
        val = ver[0].strip()
        tagged_dict[tag_name].append(val)
        text = re.sub(val, tag_name, text, count=1)
    return text


def replace_enumeration(text, tagged_dict):
    tag_name = TAG_PREFIX + r'NUMBER' + TAG_SUFFIX
    enums = re.findall(r'(^\d+\.)\s?\w+', text)
    for enum in enums:
        if not enum or not len(enum):
            continue
        val = ''.join(enum).strip()
        tagged_dict[tag_name].append(val)
        text = re.sub(val, tag_name, text, count=1)
    return text


def replace_hyphenated_terms(text, tagged_dict):
    tag_name = TAG_PREFIX + r'SPLHYPHENATEDTERM' + TAG_SUFFIX
    if len(re.findall(r'\-', text)) < 2:
        return text
    hyphenated_terms = re.findall(r'(<\w+>)((\-)(\w+))+', text, re.IGNORECASE)
    for hyph_term in hyphenated_terms:
        tagged_dict[tag_name].append(''.join(hyph_term).strip())
    return re.sub(r'(<\w+>)((\-)(\w+))+', tag_name, text, re.IGNORECASE)


def replace_phrases(text, tagged_dict):
    tag_name = TAG_PREFIX + r'DOMAINPHRASE' + TAG_SUFFIX
    hyphenated_terms = re.findall(r'(\w+(\-\w+)+)', text)
    for hyph_term in hyphenated_terms:
        if not len(hyph_term):
            continue
        val = ''.join(hyph_term[0]).strip()
        if is_common_phrase(val.replace('-', ' ')):
            continue
        if len(non_dictionary_words(val.replace('-', ' '))) == len(val.split('-')):
            tagged_dict[TAG_PREFIX + r'UNKNOWN' + TAG_SUFFIX].append(val)
            text = re.sub(val, TAG_PREFIX + r'UNKNOWN' + TAG_SUFFIX, text, count=1)
            continue
        # if val.replace('-', ' ').islower():
        #     tagged_dict[TAG_PREFIX + r'UNKNOWN' + TAG_SUFFIX].append(val)
        #     text = re.sub(val, TAG_PREFIX + r'UNKNOWN' + TAG_SUFFIX, text, count=1)
        #     continue
        tagged_dict[tag_name].append(val)
        text = re.sub(val, tag_name, text, count=1)
    return text


def replace_org_names(text, tagged_dict):
    tag_name = TAG_PREFIX + r'COMPANYNAME' + TAG_SUFFIX
    org_names = re.findall(r'((\w+)\s(enterprises|enterprise|technoloy|technologies|'
                           r'services|pvt ltd|private limited|clinic|hospitals|hospital)'
                           r'(pvt ltd|private limited)?)',
                           text, flags=re.IGNORECASE)
    for org in org_names:
        tagged_dict[tag_name].append(''.join(org).strip())
    return re.sub(r'((\w+)\s(enterprise|enterprises|technoloy|technologies|'
                  r'pvt ltd|private limited|clinic|hospitals|hospital)'
                  r'(pvt ltd|private limited)?)',
                  tag_name, text, flags=re.IGNORECASE)


def is_tag(text):
    return TAG_SUFFIX in text


def tag_spacy_entities(entities, sent, tagged_dict, tags=None):
    for entity in entities:
        if tags and entity[0] not in tags:
            continue
        tag = entity[0]
        value = entity[1]
        # if is_dict_word(value):
        #     continue
        if value.strip():
            if is_common_phrase(value):
                continue
            matches = re.findall(value, sent, re.IGNORECASE)
            if not matches:
                return sent
            if tag == u'DATE':
                tag = u'PERIOD'
            elif tag == u'GPE':
                tag = u'LOCALITY'
            elif tag == u'ORG' or u'PERSON':
                tag = u'NAMEDENTITY'
            # elif tag == u'ORG':
            #     tag = u'COMPANY'
            # elif tag == u'PERSON':
            #     tag = u'NAMEDENTITY'
            tag = TAG_PREFIX + tag.replace('_', '').upper().strip() + TAG_SUFFIX
            sent = re.sub(value, tag, sent, count=1)
            tagged_dict[tag].append(value)
    return sent


# def tag_more_entities(text, entities, tagged_dict):
#     new_ents = list()
#     tag_name = TAG_PREFIX + r'NAMEDENTITY' + TAG_SUFFIX
#     tagged_values = sorted({x for v in tagged_dict.itervalues() for x in v})
#     for entity in entities:
#         entity = ' '.join(entity)
#         if not nltk_utils.non_dictionary_words(entity):
#             continue
#         if entity in tagged_values:
#             continue
#         if TAG_SUFFIX in entity:
#             continue
#         if entity in text:
#             text = text.replace(entity, tag_name)
#             tagged_dict[tag_name].append(entity)
#             new_ents.append(entity)
#     return text, new_ents


def tag_terms(text, tag, tagged_dict, terms=None):
    if not terms:
        return text
    regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, terms)), flags=re.IGNORECASE)
    for term in regex.findall(text):
        tagged_dict[tag].append(''.join(term).strip())
    text = regex.sub(tag, text)
    return text


def remove_tagged_terms(text):
    return re.sub(TAG_PREFIX + r'([A-Z0-9_]+)' + TAG_SUFFIX, r'', text)


def replace_unknown_terms(text, tagged_dict):
    tag_name = TAG_PREFIX + 'UNKNOWN' + TAG_SUFFIX
    pattern = r'((\w+\.)+[a-zA-Z$]+)'
    unknowns = re.findall(pattern, text)
    for unk in unknowns:
        if not len(unk):
            continue
        val = ''.join(unk[0]).strip()
        tokens = val.split('.')
        if len(tokens) <= 4:
            common_words = [token for token in tokens if is_common_phrase(token)]
            if len(common_words) >= len(tokens) * 0.5:
                continue
        tagged_dict[tag_name].append(val)
        text = re.sub(re.escape(val), tag_name, text, count=1)
    return text


def tag_non_dictionary_word(text, tagged_dict):
    candidates = get_ndw_candidates(text)
    ndw_terms = list()
    unknown_terms = list()
    for term in candidates:
        if term in set(string.punctuation):
            continue
        if term.isdigit():
            continue
        segmented_terms = segment_text(term)
        segmented_terms = [term for term in segmented_terms if len(term) > 2]
        if len(segmented_terms) > 1:
            ndws = non_dictionary_words(' '.join(segmented_terms))
            if len(ndws) < len(segmented_terms):
                unknown_terms.append(term)
                continue
        if not is_dict_word(term):
            ndw_terms.append(term)
    text = tag_terms(text, tag=TAG_PREFIX + 'NDW' + TAG_SUFFIX, tagged_dict=tagged_dict, terms=ndw_terms)
    text = tag_terms(text, tag=TAG_PREFIX + 'UNKNOWN' + TAG_SUFFIX, tagged_dict=tagged_dict, terms=unknown_terms)
    return text


def get_ndw_candidates(text):
    text = remove_tagged_terms(text)
    if text:
        text = [t.strip() for t in text.split() if t.strip()]
    candidates = list()
    for candidate in text:
        candidate = candidate.strip()
        if not candidate:
            continue
        if candidate.strip()[-1] in string.punctuation and candidate.strip()[-1] not in (')', '}', ']'):
            candidate = candidate[:-1]
            if not candidate:
                continue
        if candidate in ["'s", "'t", "'d", "'ll", "'m"]:
            continue
        candidates.append(candidate)
    return candidates


def reoroder_tag_list(tokens, tags):
    tag_order = list()
    for tag in tags:
        tag_d = dict()
        if tag.split()[0] not in tokens or tag.split()[-1] not in tokens:
            return tags
        tag_d['first'] = tokens.index(tag.split()[0])
        tag_d['last'] = tokens.index(tag.split()[-1])
        tag_d['tag'] = tag
        tag_order.append(tag_d)
    tag_order = multikeysort(tag_order, ['first', '-last'])
    return [item['tag'] for item in tag_order]
