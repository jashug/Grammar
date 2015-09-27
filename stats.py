import pickle
import webbrowser
import os.path
import json
import question_basics
from questions import kanjiQuestions as kanji, vocabQuestions as vocab
from questions import grammarQuestions as grammar

priority_spec = [('gai', '%d', 3), ('spec', '%d', 3), ('ichi', '%d', 3),
                 ('news', '%d', 3), ('nf', '%02d', 49)]
pri_map = {}
for pref, index, num in priority_spec:
    for i in range(1, num):
        pri_map[pref + index % i] = (pref, i)

def question_repr(question):
    output = {}
    if isinstance(question, question_basics.CategoryQuestion):
        output['__class__'] = question.__class__.__name__
    elif issubclass(question, question_basics.CategoryQuestion):
        output['__class__'] = question.__name__
    else:
        raise TypeError("Not a CategoryQuestion", question)
    if hasattr(question, 'head'):
        output['head'] = question.head
    if isinstance(question, kanji.KanjiToEnglishQuestion):
        output['jlpt'] = question.jlpt
        output['grade'] = question.grade
        output['freq'] = question.freq
        output['strokes'] = question.strokes
    elif isinstance(question, (vocab.VocabKtoSQuestion,
                               vocab.VocabKtoRQuestion,
                               vocab.VocabRtoSQuestion)):
        #output['entries'] = list(question.entries.items())
        output['pris'] = {pref:num for pref, index, num in priority_spec}
        for entry in question.entries:
            for pri in entry[2]:
                pref, i = pri_map[pri]
                output['pris'][pref] = min(output['pris'][pref], i)
    elif isinstance(question, grammar.WordQuestion):
        output['head'] = output['rep'] = question.rep
        #output['answers'] = question.verifier.values
    return output

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, frozenset) or isinstance(obj, set):
            output = list(obj)
        elif (isinstance(obj, question_basics.CategoryQuestion) or
              issubclass(obj, question_basics.CategoryQuestion)):
            output = question_repr(obj)
        else:
            output = json.JSONEncoder.default(self, obj)
        return output

def get_stats(pack):
    assert pack.feed.ordered[-1] is None

    data = {
        'feed':
        {
            'ordered':pack.feed.ordered[:-1],
            'mapping':pack.feed.mapping,
            'seen':pack.feed.seen
        },
        'triage':{
        },
        'scheduler':{
        },
        'context':pack.context,
    }

    stats_template_path = os.path.join(os.path.dirname(__file__),
                                       'stats_template.html')
    with open(stats_template_path, 'r') as f:
        stats_template = f.read()
    encoded_data = json.dumps(data, cls=MyEncoder).replace('</', r'<\/')
    return stats_template.replace('####data####', encoded_data)

if __name__ == '__main__':
    pack_path = os.path.join(os.path.dirname(__file__), 'records', 'pack.pkl')
    stats_path = os.path.join(os.path.dirname(__file__), 'records', 'stats.html')
    with open(pack_path, 'rb') as f:
        pack = pickle.load(f)
    stats = get_stats(pack)
    with open(stats_path, 'w') as f:
        f.write(stats)
    #webbrowser.open_new("file://"+stats_path)
