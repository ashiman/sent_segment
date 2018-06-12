from __future__ import print_function
from sent_segment.preprocessor import segment_sentences
from sent_segment import spacy_utils



def sentence_segmentation(data, contexts= None, delims = None):
    # req = request.get_json()
    # logger.info({'request': req, 'api': 'sentence_segmentation', 'type': 'POST'})
    # payload = req.get('data', None)
    # contexts = req.get('contexts', None)
    # delims = req.get('delims', None)
    segmented_texts = list()
    payload = data
    # contexts = None
    # delims = None

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
        segmented_text['segmented_text'] = segment_sentences(p, strip=False, context=context, delim=delim)
        segmented_texts.append(segmented_text)
    return segmented_texts


if __name__ == "__main__":
    data = ["Wooo!! it was a great show. Meet me at 10am tomorrow.","What's up ?? Lets catch up"]
    segmented_sentences = sentence_segmentation(data)
    # parsed = spacy_utils.parse_text(data)

    print(segmented_sentences)
