## Sentence Segmentation.

# How to use??
Example :

    from sent_segment.language_utility import sentence_segmentation
    sen = sentence_segmentation(["hey. what's up?"]) # list of sentences as argument
    # other way is to pass list of sentences and spacy parser as arguments
    # import spacy
    # nlp = spacy.load('en')
    # sen = sentence_segmentation(["hey. what's up?"], nlp)
    print (sen)


Output :
[{'paragraph': "hey. what's up?", 'segmented_text': ['hey.', "what's up?"]}]
