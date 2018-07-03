from __future__ import print_function
import sent_segment
from sent_segment.preprocessor import segment_sentences
from sent_segment import spacy_utils


# from sent_segment import nlp


def sentence_segmentation(data, parser=None, contexts=None, delims=None):
    # req = request.get_json()
    # logger.info({'request': req, 'api': 'sentence_segmentation', 'type': 'POST'})
    # payload = req.get('data', None)
    # contexts = req.get('contexts', None)
    # delims = req.get('delims', None)
    segmented_texts = list()
    payload = data
    # contexts = None
    # delims = None

    if not sent_segment.nlp:
        if not parser:
            sent_segment.nlp = spacy_utils.load_model()
            parser = sent_segment.nlp
        else:
            sent_segment.nlp = parser
    else:
        parser = sent_segment.nlp


    for idx, p in enumerate(payload):
        segmented_text = dict()
        segmented_text['paragraph'] = p
        context = None
        if contexts:
            try:
                context = contexts[idx]
            except IndexError:
                pass
        delim = None
        if delims:
            try:
                delim = delims[idx]
            except IndexError:
                delim = None
        segmented_text['segmented_text'] = segment_sentences(p, parser, strip=False, context=context, delim=delim)
        segmented_texts.append(segmented_text)
    return segmented_texts


if __name__ == "__main__":
    data = ["Wooo!! it was a great show at 2 a.m. in farms. Go to the voot.com."]
    parser = spacy_utils.parser
    segmented_sentences = sentence_segmentation(data)

    # parsed = spacy_utils.parse_text(data)

    print(segmented_sentences)
