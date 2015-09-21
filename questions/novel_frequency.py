import os.path
from collections import namedtuple, defaultdict
import questions.kanjiQuestions as kanjiq
import questions.vocabQuestions as vocabq
from question_basics import surrogateescape

Record = namedtuple('Record', ['count', 'word', 'pos'])
def parse_freq():
    path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'BigDataFiles', 'base_aggregates.txt')
    records = []
    with open(path, 'r', encoding='utf_8') as f:
        for line in f:
            assert line[-1] == '\n'
            line = line[:-1]
            assert '\n' not in line
            count, word, pos = line.split('\t')
            count, word, pos = int(count), word, frozenset(pos.split(','))
            records.append(Record(count, word, pos))
    return records

def get_freq():
    records = parse_freq()
    records = [r for r in records if '記号' not in r.pos]
    remove = {'未知語', '助詞', '助動詞', 'フィラー', 'その他',
              '感動詞', '接続詞', '接頭詞',
             }
##    records = [Record(r.count, r.word, frozenset(p for p in r.pos
##                                                 if p not in remove))
##               for r in records]
##    records = [r for r in records if r.pos]

    records = [r for r in records if any(p not in remove for p in r.pos)]
    
##    records = [r for r in records if all(p not in remove for p in r.pos)]
    records.reverse()
    return records

def get_components():
    path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'BigDataFiles', 'kradfile-u.txt')
    components = {}
    with open(path, 'r', encoding='utf_8') as f:
        for line in f:
            if line.startswith('#'):
                # comment line
                continue
            assert line[-1] == '\n'
            line = line[:-1]
            assert '\n' not in line
            kanji, sub_components = line.split(' : ')
            sub_components = set(sub_components.split(' '))
            assert kanji not in components
            components[kanji] = sub_components
    def done():
        for k in components:
            for k2 in components[k]:
                if k2 in components:
                    for k3 in components[k2]:
                        if k3 not in components[k]:
                            return False
        return True
    #i = 0
    while not done(): # 2 iterations
        for k in components:
            for k2 in list(components[k]):
                if k2 in components:
                    components[k].update(components[k2])
        #i += 1
        #print(i)
    #print("Iterations:", i)
    remove = "囗毋" # only need non-radical versions
    for rem in remove:
        if rem in components:
            del components[rem]
        for k in components:
            if rem in components[k]:
                components[k].remove(rem)
    return components

def get_questions():
    records = get_freq()
    components = get_components()
    kana = kanjiq.get_kana()
    kanji = kanjiq.get_kanji()
    vocab = vocabq.get_vocab()
    d = {}
    for r in records:
        d[r.word] = r.count
    # only use vocab we have frequency for (~50,000 questions)
    vocab = [q for q in vocab if q.head in d]
    vocab.sort(key=lambda q:d[q.head], reverse=True)
    kanji = {q.head:q for q in kanji}
    #print("Got materials.")
    
    used = set()
    questions = []
    def add(q):
        used.add(q)
        questions.append(q)
    def dfs(c):
        if c not in kanji:
            return # skip non-kanji radicals
        if kanji[c] in used:
            return # done, or in progress
        used.add(kanji[c])
        if c in components:
            for c2 in components[c]:
                dfs(c2)
        questions.append(kanji[c])

    for q in kana:
        add(q)
    kana = set(q.head for q in kana)
    for q in vocab:
        if q.head in kanji and isinstance(q, vocabq.VocabKtoSQuestion):
            # prune duplicated kanji and vocabKtoS questions
            kanji[q.head].answers += q.verifier.values
            continue
        if not all(c in kana or c in kanji
                   for c in kanjiq.iterate_with_yoon(q.head)):
            # Uses characters we don't teach, so skip
            continue
        for c in kanjiq.iterate_with_yoon(q.head):
            if c in kanji:
                dfs(c) # teach kanji and components first
        add(q)
    return questions

if __name__ == '__main__':
    questions = get_questions()
