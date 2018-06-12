# Language to script mapping
lang_script = {
    'hindi': 'devanagari',
    'marathi': 'devanagari',
    'rajasthani': 'devanagari',
    'konkani': 'devanagari',
    'kannada': 'kannada',
    'gujarati': 'gujarati',
    'punjabi': 'gurmukhi',
    'oriya': 'oriya',
    'tamil': 'tamil',
    'telugu': 'telugu',
    'malayalam': 'malayalam',
    'bengali': 'bengali',
    'assamese': 'bengali',
    'english': 'english'
}

# Script to unicode block mapping
unicode_blocks = {
    'devanagari': (0x0900, 0x097f),
    'kannada': (0x0c80, 0x0cff),
    'bengali': (0x0980, 0x09ff),
    'gurmukhi': (0x0a00 - 0x0a7f),
    'gujarati': (0x0a80, 0x0aff),
    'oriya': (0x0b00, 0x0b7f),
    'tamil': (0x0b80, 0x0bff),
    'telugu': (0x0c00, 0x0c7f),
    'malayalam': (0x0d00, 0x0d7f)
}

# Allowed puncts. Used in preprocessing text before building models.
# Change suitably based on your requirements.
punkt = list('.,!%$&?')
whitespace = list(' \n')
