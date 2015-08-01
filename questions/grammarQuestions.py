# coding=utf-8

import cPickle as pickle
import base64
from textwrap import dedent
from builder import CategoryQuestion, Literal, QuestionThunk

def uid(s):
    """Generate a unique ASCII string for a unicode string."""
    return base64.urlsafe_b64encode(s.encode("UTF-8"))

class TranslationQuestion(CategoryQuestion):
    @property
    def prompt(self):
        return "Translate: %s" % self.rep

class Word(TranslationQuestion):
    q = staticmethod(lambda word, values:'Word.'+uid(word))
    def __init__(self, get, word, values):
        self.values = values
        self.rep = word
        self.parts = [Literal(values, self)]
        self.body = ("The word '%s' can be translated as:\n" % word +
                     '\n'.join(values))
WordQuestion = lambda word, values:QuestionThunk(Word, word, values)

class Conjugatable(TranslationQuestion):
    q = staticmethod(lambda word, values, suffix:'Conj.'+uid(word))
    def __init__(self, get, word, values, suffix):
        self.values = values
        self.suffix = suffix
        self.rep = word
        assert all(val.endswith(suffix) for val in values)
        stems = [val[:-len(suffix)] for val in values]
        self.parts = [Literal(stems, self), Literal([suffix], self)]
        self.body = ("The word '%s' can be translated as:\n" % word +
                     '\n'.join(values))
ConjugatableQuestion = (lambda word, values, suffix:
                        QuestionThunk(Conjugatable, word, values, suffix))

class Declarative(TranslationQuestion):
    q = "DeclareDa"
    body = u"Declare 'is X' with 'Xだ'."
    def __init__(self, get):
        self.obj = get('noun')
        self.rep = "is %s" % self.obj.rep
        self.parts = [self.obj, Literal([u'だ'], self)]

class NegativeNoun(TranslationQuestion):
    q = "NegNoun"
    body = dedent(u"""\
        Form 'is not X' with 'Xでわない' or 'Xじゃない'.
        Xじゃない is the more casual form.""")
    def __init__(self, get):
        self.obj = get('noun')
        self.rep = "is not %s" % self.obj.rep
        self.parts = [self.obj,
                      Literal([u'でわ', u'じゃ'], self),
                      Literal([u'ない'], self)]

class PastNoun(TranslationQuestion):
    q = "PastNoun"
    body = u"Form 'was X' with 'Xだった'."
    def __init__(self, get):
        self.obj = get('noun')
        self.rep = "was %s" % self.obj.rep
        self.parts = [self.obj, Literal([u'だった'], self)]

grammar = [
    (Declarative, 'undec'),
    (NegativeNoun, 'neg'),
    (PastNoun, 'undec'),
]
global_categories = {}

def expand(categories, cat):
    if cat in categories:
        new = set()
        for group in categories[cat]:
            new.update(expand(categories, group))
        categories[cat] = new
        return new
    else:
        return set([cat])
    
suffixes = {
}

def addQuestions(qs, dictCache=None):
    categories = global_categories.copy()
    if dictCache is None:
        raise Exception("Need Cache")
    with open(dictCache, 'rb') as f:
        dictionary, baseCategories = pickle.load(f)
    for cat in baseCategories:
        assert cat not in categories
        categories[cat] = baseCategories[cat]
    for cat in categories:
        expand(categories, cat)

    dictionary_list = []
    rank_dict = {}
    for word in dictionary:
        values, group, rank = dictionary[word]
        dictionary_list.append((word, values, group))
        rank_dict[word] = rank
    dictionary_list.sort(key=lambda (word, values, group): rank_dict[word])

    ordered = []
    rank_dict = {}
    def add(group, rank, question):
        q = question.q
        assert q not in qs
        ordered.append((q, group))
        rank_dict[q] = rank
        qs[q] = question
    for i in range(len(dictionary_list)):
        word, values, group = dictionary_list[i]
        if group in suffixes:
            question = ConjugatableQuestion(word, values, suffixes[group])
        else:
            question = WordQuestion(word, values)
        add(group, (i, 0), question)
    for i in range(len(grammar)):
        question, group = grammar[i]
        add(group, (1 * i, 1), question)
    
    ordered.sort(key=lambda (q, group):rank_dict[q])
    return ordered, categories
