## Preprocessor and Entity Tagger

Rosetta's preprocessor and entity tagger has the following steps:

- clean and normalize the text
- tag regex based entities
- segment sentences
- replace regex tags with their values
- for each sentence
    - tag regex bases entities
    - tag entities from the knowledge base
    - tag spacy entities (for classes that are allowed)
    - tag non-dictionary words and other names entities
- return tagged text along with a dictionary of tags and their values.


### Modules

`tagger.py` has all the regex based tagger implementations

`preprocess.py` has the overall flow and the Elastic query creation logic