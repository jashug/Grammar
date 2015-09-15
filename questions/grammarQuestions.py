# coding=utf-8

import pickle
import base64
import copy
import enum
from collections import defaultdict
from textwrap import dedent
from question_basics import CategoryQuestion, Literal, uid, Category

class GramamrCategory(object):
    def __init__(self, groups, predicate_type):
        self.groups = set(groups)
        self.predicate_type = predicate_type

    def __repr__(self):
        return "GrammarCategory(%r, %r)" % (self.groups, self.predicate_type)

    def __call__(self, group):
        return group in self.groups

class PredicateTypes(enum.Enum):
    pass
any_predicate = set(PredicateTypes)

class TranslationQuestion(CategoryQuestion):
    @property
    def prompt(self):
        return "Translate: %s" % self.rep

class WordQuestion(TranslationQuestion):
    def __init__(self, word, values, group):
        self.q = 'Word.'+uid(word)
        self.group = group
        self.values = values
        self.rep = word
        self.parts = [Literal(values)]
        self.body = ("The word '%s' can be translated as:\n" % word +
                     '\n'.join(values))

    def child_categories(self, predicate=any_predicate):
        return ()

    def __call__(self):
        self = copy.deepcopy(self)
        super(WordQuestion, self).__init__()
        return self

##class ConjugatableQuestion(TranslationQuestion):
##    def __init__(self, word, values, suffix):
##        self.q = 'Conj.'+uid(word)
##        self.values = values
##        self.suffix = suffix
##        self.rep = word
##        assert all(val.endswith(suffix) for val in values)
##        stems = [val[:-len(suffix)] for val in values]
##        self.parts = [Literal(stems), Literal([suffix])]
##        self.body = ("The word '%s' can be translated as:\n" % word +
##                     '\n'.join(values))
##
##    def child_categories(self, predicate=any_predicate):
##        return ()
##
##    def __call__(self):
##        self = copy.deepcopy(self)
##        super(ConjugatableQuestion, self).__init__()
##        return self

##class Declarative(TranslationQuestion):
##    q = "DeclareDa"
##    body = "Declare 'is X' with 'Xだ'."
##    group = frozenset(('undec',))
##    def __init__(self, obj):
##        super().__init__(obj)
##        self.rep = "is %s" % obj.rep
##        self.parts = [obj, Literal(['だ'])]
##
##    @staticmethod
##    def child_categories(predicate=any_predicate):
##        return ((global_filters['noun'], ()),)
##
##class NegativeNoun(TranslationQuestion):
##    q = "NegNoun"
##    body = dedent("""\
##        Form 'is not X' with 'Xでわない' or 'Xじゃない'.
##        Xじゃない is the more casual form.""")
##    group = frozenset(('neg', 'noun'))
##    def __init__(self, obj):
##        super().__init__(obj)
##        self.rep = "not %s" % obj.rep
##        self.parts = [obj,
##                      Literal(['でわ', 'じゃ']),
##                      Literal(['ない'])]
##
##    @staticmethod
##    def child_categories(predicate=any_predicate):
##        return ((global_filters['noun'], ()),)
##
##class PastNoun(TranslationQuestion):
##    q = "PastNoun"
##    body = "Form 'was X' with 'Xだった'."
##    group = frozenset(('undec',))
##    def __init__(self, obj):
##        super().__init__(obj)
##        self.rep = "was %s" % obj.rep
##        self.parts = [obj, Literal(['だった'])]
##
##    @staticmethod
##    def child_categories(predicate=any_predicate):
##        return ((global_filters['noun'], ()),)
##
##class NegPast(TranslationQuestion):
##    q = "NegPast"
##    body = dedent("""\
##        The negative form of just about everything ends in 'ない'.
##        Form 'not X (past)' from 'not X' by replacing
##        'ない' with 'なかった'.""")
##    group = frozenset(('negpast'))
##    def __init__(self, obj):
##        super().__init__(obj)
##        self.rep = "%s (past)" % obj.rep
##        if obj.parts[-1].values != ['ない',]:
##            print(obj, obj.parts, obj.parts[-1].values)
##        assert obj.parts[-1].values == ['ない',]
##        self.parts = obj.parts[:-1] + [Literal(['なかった',])]
##
##    @staticmethod
##    def child_categories(predicate=any_predicate):
##        return (category.without('negpast') & Tag('neg'),)

grammar = [
]
global_categories = {
}
global_filters = {}

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
    for cat in categories:
        global_filters[cat] = Category(categories[cat])

    dictionary_list = []
    rank_dict = {}
    for word in dictionary:
        values, group, rank = dictionary[word]
        dictionary_list.append((word, values, group))
        rank_dict[word] = rank
    dictionary_list.sort(key=lambda word_values_group: rank_dict[word_values_group[0]])

    ordered = []
    rank_dict = {}
    def add(rank, question):
        q = question.q
        group = question.group
        assert q not in qs
        ordered.append((q, group))
        rank_dict[q] = rank
        qs[q] = question
    for i in range(len(dictionary_list)):
        word, values, group = dictionary_list[i]
        if group in suffixes:
            question = ConjugatableQuestion(word, values, group)
        else:
            question = WordQuestion(word, values, group)
        add((i, 0), question)
    for i in range(len(grammar)):
        question = grammar[i]
        add((1 * i, 1), question)
    
    ordered.sort(key=lambda q_group:rank_dict[q_group[0]])
    return ordered
