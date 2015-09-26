# coding=utf-8

import os.path
import pickle
import base64
import copy
import enum
import itertools
from collections import defaultdict
from textwrap import dedent
from question_basics import (
    CategoryQuestion, Literal, uid, Category,
    SimpleLeafQuestion,
    )
from maxflow import SOURCE, SINK, FlowGraph

class PredicateTypes(enum.Enum):
    NOUN = 'n'
any_predicate = set(PredicateTypes)

class TranslationQuestion(CategoryQuestion):
    @property
    def prompt(self):
        return "Translate: %s" % self.rep

class WordQuestion(SimpleLeafQuestion, TranslationQuestion):
    def __init__(self, word, values, group):
        super().__init__()
        self.group = group
        self.verifier = Literal(values)
        self.rep = word

    @property
    def q(self):
        return 'Word.'+uid(self.rep)

    @property
    def body(self):
        return ("Word: %s\n" % self.rep +
                "Part of speech: %s\n" % set(self.group) +
                "Translation: %s" % self.verifier.values[0] +
                ("\nAlternate Translations: %s" %
                 '; '.join(self.verifier.values[1:])
                 if len(self.verifier.values) > 1 else ""))

    @property
    def primary_translation(self):
        return self.verifier.values[0]

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

class Declarative(TranslationQuestion):
    q = "DeclareDa"
    body = dedent("""\
        Declare a sentence 'X (declared)' by saying 'Xだ'.
        The sentence must end in an unconjugated noun or na-adjective.""")
    group = frozenset()
    def __init__(self, obj):
        super().__init__(obj)
        self.rep = "is %s" % obj.rep
        self.parts = [obj, Literal(['だ'])]

    @staticmethod
    def child_categories(predicate=any_predicate):
        return ((categories['noun'], (PredicateTypes.NOUN,)),)

class NegativeNoun(TranslationQuestion):
    q = "NegNoun"
    body = dedent("""\
        Form a negative noun 'not X' with 'Xでわない' or 'Xじゃない'.
        Xじゃない is the more casual form.
        This conjugates as an i-adjective.""")
    group = frozenset(('adj-i',))
    def __init__(self, obj):
        super().__init__(obj)
        self.rep = "not %s" % obj.rep
        self.parts = [obj,
                      Literal(['でわ', 'じゃ']),
                      Literal(['な']),
                      Literal(['い'])]

    @staticmethod
    def child_categories(predicate=any_predicate):
        return ((categories['noun'], ()),)

class PastNoun(TranslationQuestion):
    q = "PastNoun"
    body = "Form the past tense of a noun: 'X (past)' with 'Xだった'."
    group = frozenset()
    def __init__(self, obj):
        super().__init__(obj)
        self.rep = "%s (past)" % obj.rep
        self.parts = [obj, Literal(['だった'])]

    @staticmethod
    def child_categories(predicate=any_predicate):
        return ((categories['noun'], ()),)

class PastIAdj(TranslationQuestion):
    q = "PastIAdj"
    body = dedent("""\
        Form the past tense of an i-adjective: "X (past)" by
        replacing the 'い' with 'かった'.""")
    group = frozenset()
    def __init__(self, obj):
        super().__init__(obj)
        self.rep = "%s (past)" % obj.rep
        if obj.parts[-1].values != ['い',]:
            print(obj, obj.parts, obj.parts[-1].values)
        assert obj.parts[-1].values == ['い',]
        self.parts = obj.parts[:-1] + [Literal(['かった',])]

    @staticmethod
    def child_categories(predicate=any_predicate):
        return ((categories['adj-i'], ()),)

grammar = [
    Declarative,
    NegativeNoun,
    PastNoun,
    PastIAdj,
]

general_categories = {
    'noun': {'n', 'n-adv', 'n-suf', 'n-pref', 'n-t'},
    'verb': {'aux-v', 'iv', 'v-unspec', 'v1', 'v1-s',
             'v2a-s', 'v2b-k', 'v2b-s', 'v2d-k', 'v2d-s',
             'v2g-k', 'v2g-s', 'v2h-k', 'v2h-s', 'v2k-k',
             'v2k-s', 'v2m-k', 'v2m-s', 'v2n-s', 'v2r-k',
             'v2r-s', 'v2s-s', 'v2t-k', 'v2t-s', 'v2w-s',
             'v2y-k', 'v2y-s', 'v2z-s', 'v4b', 'v4g', 'v4h', 'v4k',
             'v4m', 'v4n', 'v4r', 'v4s', 'v4t', 'v5aru', 'v5b',
             'v5g', 'v5k', 'v5k-s', 'v5m', 'v5n', 'v5r', 'v5r-i',
             'v5s', 'v5t', 'v5u', 'v5u-s', 'v5uru', 'vi', 'vk',
             'vn', 'vr', 'vs', 'vs-c', 'vs-i', 'vs-s', 'vt', 'vz',
            },
}
categories = {}
def expand(categories, cat):
    if cat in categories:
        new = set()
        for group in categories[cat]:
            new.update(expand(categories, group))
        categories[cat] = new
        return new
    else:
        return set([cat])
def setup_categories(groups):
    categories.clear()
    categories.update(general_categories)
    groups = set(groups)
    for group in groups:
        for part in group:
            assert part not in general_categories
            if part not in categories:
                categories[part] = set()
            categories[part].add(group)
    for cat in categories:
        expand(categories, cat)
    for cat in categories:
        categories[cat] = Category(categories[cat])
groups_path = os.path.join(os.path.dirname(__file__), 'groups.pkl')
def save_groups(groups):
    with open(groups_path, 'wb') as f:
        pickle.dump(groups, f)
def load_groups():
    try:
        with open(groups_path, 'rb') as f:
            groups = pickle.load(f)
    except FileNotFoundError:
        print("No groups found")
        groups = set()
    return groups
groups = load_groups()
setup_categories(groups)

suffixes = {
}

def get_words():
    path = os.path.join(os.path.dirname(__file__), 'grammarPickle.pkl')
    with open(path, 'rb') as f:
        dictionary = pickle.load(f)
    words = []
    groups = set()
    for word in dictionary:
        values, group = dictionary[word]
        if group in suffixes:
            words.append(ConjugatableQuestion(word, values, group))
        else:
            words.append(WordQuestion(word, values, group))
        groups.add(group)
    for question in grammar:
        groups.add(question.group)
    save_groups(groups)
    setup_categories(groups)
    return words

def get_grammar(words):
    questions = []
    group_counts = {group:0 for group in groups}
    graph = FlowGraph()
    category_counter = itertools.count()
    def can_block(graph, category):
        graph_copy = graph.copy()
        target = 0
        for group in groups:
            if category(group) and group_counts[group] > 0:
                graph_copy.add_edge(group, SINK, group_counts[group])
                target += group_counts[group]
        return graph_copy.compute_max_flow() == target
    def add_constraint(graph, category):
        node = next(category_counter)
        graph.add_edge(SOURCE, node, 1)
        for group in groups:
            if category(group):
                graph.add_edge(node, group, 1)
    i = 0
    children = None
    for word in words:
        #print("Word", word.prompt, word.group)
        group_counts[word.group] += 1
        concepts = []
        while i < len(grammar):
            graph_copy = graph.copy()
            children = grammar[i].child_categories()
            children = [category for category, data in children]
            for category in children:
                if can_block(graph_copy, category):
                    break
                add_constraint(graph_copy, category)
            else:
                #print("Concept", grammar[i].group)
                concepts.append(grammar[i])
                group_counts[grammar[i].group] += 1
                graph = graph_copy
                children = None
                i += 1
                continue
            break
        questions.append((word, concepts))
    #print(group_counts)
    return questions
