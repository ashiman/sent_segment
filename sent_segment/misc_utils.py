import numpy as np
from html.parser import HTMLParser
from functools import cmp_to_key


def get_quantile(nums, q):
    return np.percentile(nums, q)


"""
Taken directly from http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys/29849371
Thanks to stackoverflow user hughdbrown
"""


def cmp(a, b):
    return (a > b) - (a < b)


def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                  (itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0

    return sorted(items, key=cmp_to_key(comparer))


"""
Adapted from the sample code here: https://docs.python.org/2/library/htmlparser.html#example-html-parser-application
"""


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    tag_list = None

    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_list = list()

    def handle_starttag(self, tag, attrs):
        self.tag_list.append('<' + tag + '>')

    def handle_endtag(self, tag):
        self.tag_list.append('</' + tag + '>')

    def handle_data(self, data):
        pass
