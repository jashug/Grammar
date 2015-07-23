import cPickle as pickle
import base64
from builder import CategoryQuestion, Literal, QuestionThunk

def uid(s):
    """Generate a unique ASCII string for a unicode string."""
    return base64.urlsafe_b64encode(s.encode("UTF-8"))

class Word(CategoryQuestion):
    q = staticmethod(lambda word, values:'Word.'+uid(word))
    def __init__(self, get, word, values):
        self.values = values
        self.rep = word
        self.prompt = "Translate %s" % self.rep
        self.parts = [Literal(values, self)]
        self.body = ("The word '%s' can be translated as:\n" % word +
                     '\n'.join(values))
WordQuestion = lambda word, values:QuestionThunk(Word, word, values)

class Conjugatable(CategoryQuestion):
    q = staticmethod(lambda word, values, suffix:'Conj.'+uid(word))
    def __init__(self, get, word, values, suffix):
        self.values = values
        self.suffix = suffix
        self.rep = word
        self.prompt = "Translate %s" % self.rep
        assert all(val.endswith(suffix) for val in values)
        stems = [val[:-len(suffix)] for val in values]
        self.parts = [Literal(stems, self), Literal([suffix], self)]
        self.body = ("The word '%s' can be translated as:\n" % word +
                     '\n'.join(values))
ConjugatableQuestion = (lambda word, values, suffix:
                        QuestionThunk(Conjugatable, word, values, suffix))

grammar = []
categories = {}

def expand(cat):
    if cat in categories:
        new = set()
        for group in categories[cat]:
            new.update(expand(group))
        categories[cat] = new
        return new
    else:
        return set([cat])
    
suffixes = {
}

def addQuestions(qs, dictCache=None):
    if dictCache is None:
        raise Exception("Need Cache")
    with open(dictCache, 'rb') as f:
        dictionary, baseCategories = pickle.load(f)
    for cat in baseCategories:
        assert cat not in categories
        categories[cat] = baseCategories[cat]
    for cat in categories:
        expand(cat)

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
        add(group, (20 * i, 1), question)
    
    ordered.sort(key=lambda (q, group):rank_dict[q])
    return ordered, categories
