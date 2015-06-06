# -*- coding: utf-8 -*-

### Experimental code to quickly find all members of a set of strings within another string.

def create_index():
    ind = [0] * 130
    ind[128] = False
    ind[129] = False
    return ind

def add_word(word, index):
    add_word_(word, index, word)

def add_word_(word, index, whole_word):
    if len(word) == 0:
        index[129] = whole_word
        return
    pos = ord(word[0])
    if pos < 128:
        if index[pos] == 0:
            index[pos] = create_index()
        add_word_(word[1:], index[pos], whole_word)
    else:
        if not index[128]:
            index[128] = {}
        if not word[0] in index[128]:
            index[128][word[0]] = create_index()
        add_word_(word[1:], index[128][word[0]], whole_word)

def find_words(text, index):
    words = set()
    for offset in range(0, len(text)):
        new_words = find_words_at_offset(text, index, offset)
        if new_words:
            words |= new_words
    return words

def find_words_at_offset(text, index, offset):
    result = None
    if index[129]:
        result = set([index[129]])
    if offset < len(text):
        pos = ord(text[offset])
        sub_result = None
        if pos < 128:
            if index[pos] != 0:
                sub_result = find_words_at_offset(text, index[pos], offset + 1)
        else:
            if index[128] and text[offset] in index[128]:
                sub_result = find_words_at_offset(text, index[128][text[offset]], offset + 1)
        if sub_result:
            if result:
                result |= sub_result
            else:
                result = sub_result
    return result

def test_substring():
    index = create_index()
    add_word("kitten", index)
    assert find_words("I am a kitten.", index) == set(["kitten"])   

def test_substrings():
    index = create_index()
    add_word("kitten", index)
    add_word("kite", index)
    add_word("kittler", index)
    assert find_words("The kitten flies a kite.", index) == set(["kitten", "kite"])    

def test_unicode():
    index = create_index()
    add_word("عبد الله محمد بن موسى الخوارزمی", index)
    add_word("algorithm", index)
    assert find_words("عبد الله محمد بن موسى الخوارزمی invented the algorithm.", index) == set(["عبد الله محمد بن موسى الخوارزمی", "algorithm"])
