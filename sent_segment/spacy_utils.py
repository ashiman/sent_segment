import re
from pprint import pprint
import spacy
# from spacy.pipeline import DependencyParser


class SpacyUtils(object):
    parser = None

    def __init__(self):
        self.parser = None

    def parse_text(self, text):
        return self.parser(text, disable=['entity', 'textcat'])

    def load_model(self):
        parser = spacy.load('en')
        return parser

    @staticmethod
    def tag_pos(parsed_text):
        pos_tags = list()
        for token in parsed_text:
            pos_tags.append((token.orth_, token.pos_))
        return pos_tags

    @staticmethod
    def get_lemmas(parsed_text):
        return [token.lemma_ for token in parsed_text]

    @staticmethod
    # def get_sentences(parsed_text):
    #     return parsed_text.sents
    def get_sentences(text_sen, parser, context=None, delim=None):
        if not text_sen:
            return []
        if context and context.lower().strip() == "address":
            if not delim:
                delim = ','
            splits = re.split(r'(' + delim + r')', text_sen)
            sents = list()
            for idx, split in enumerate(splits):
                if split == delim:
                    continue
                if idx + 1 < len(splits) and splits[idx + 1] == delim:
                    sents.append(split.strip() + delim)
                else:
                    sents.append(split.strip())
            return sents

        # sbd = parser.create_pipe('sentencizer')
        # parser.add_pipe(sbd)
        # parser = DependencyParser()
        parsed_text = parser(text_sen)
        sentences = []
        for sent in parsed_text.sents:
            sentences.append(sent.text)

        return sentences

    @staticmethod
    def tag_entities(parsed_text):
        entities = list(parsed_text.ents)
        return [(entity.label_, ' '.join(t.orth_ for t in entity)) for entity in entities]

    @staticmethod
    def derive_entities(pos_tags):
        propns = [idx for idx, tag in enumerate(pos_tags) if tag[1] == u'PROPN']
        entities = list()
        i = 0
        while i < len(propns):
            entity = list()
            term = pos_tags[propns[i]][0]
            entity.append(term)
            if term.endswith('.') or 'xxx' in term.lower():
                break
            start_idx = propns[i]
            for j in range(i + 1, len(propns)):
                if not propns[j] == start_idx + 1:
                    break
                term = pos_tags[propns[j]][0]
                entity.append(term)
                start_idx += 1
                if term.endswith('.') or 'xxx' in term.lower():
                    break
            i += len(entity)
            if len(entity) >= 2 and 'xxx' not in ''.join(entity).lower():
                entities.append(entity)
        return entities

    @staticmethod
    def normalize_slang(parsed_text):
        return [(token.orth_, token.lemma_) for token in parsed_text]

    @staticmethod
    def get_similar(term):
        return

    @staticmethod
    def get_terms_connected_by_dependency(sentence, term):
        """
        This method returns all the terms dependen to the input term in the given sentence.
        :param sentence: Given sentence
        :param term: Given term
        :return: Liste of terms dependant to "term"
        """
        parser = English()
        parsedEx = parser(sentence)
        # shown as: original token, dependency tag, head word, left dependents, right dependents
        connected_words = set()
        for token in parsedEx:
            if token.orth_ == term or token.head.orth_ == term:
                #print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts],
                #      [t.orth_ for t in token.rights])
                connected_words.add(token.orth_)
                connected_words.add(token.head.orth_)

        if connected_words.__contains__(term):
            connected_words.remove(term)
        if len(connected_words) == 0:
            connected_words = None
        return connected_words

        """
        parser = parser.Parser()
        tokens = "Set the volume to zero when I 'm in a meeting unless John's school calls".split()
        tags, heads = parser.parse(tokens)
        print heads
        #[-1, 2, 0, 0, 3, 0, 7, 5, 7, 10, 8, 0, 13, 15, 15, 11]
        for i, h in enumerate(heads):
            head = tokens[heads[h]] if h >= 1 else 'None'
            print(tokens[i] + ' <-- ' + head)
        """


if __name__ == "__main__":
    txt = u"Celebrating XXXXX years.! Chicken Biryani for just Rs.XXXXX " \
          u"Download rosetta https:\/\/goo.gl\/SlJagx. " \
          u"Travel getting expensive?Don't worry XXXXXRide is here." \
          u"Now share a ride in \"your\" car\/bike\/auto\/taxi&save your travel cost." \
          u"Download www.gs.im\/m\/?t=srhLTKBXXXXXjcR " \
          u"PHONE-A-FRIEND:Looking for Friendship & Dating service in your area? " \
          u"Plz call SANA @ XXXXX \/ XXXXX XXXXX% Privacy. www.minglewoo.com"

    text = u"Godrej Properties:For a special preview of Godrej Avenues,Yelahanka,B'luru " \
           u"visit us @Ramanashree California Resort. Starting @Rs.XXXXXlacs. Missed call:XXXXX"
    spacy_utils = SpacyUtils()
    parsed = spacy_utils.parse_text(text)
    pprint(spacy_utils.tag_entities(parsed))
    pprint(spacy_utils.derive_entities(spacy_utils.tag_pos(parsed)))
    pprint(spacy_utils.get_sentences(txt, context=None, delim=None))
