import os.path
from collections import namedtuple, defaultdict

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

if __name__ == '__main__':
    import questions.kanjiQuestions as kanjiq
    import questions.vocabQuestions as vocabq
    records = get_freq()
    kanji = kanjiq.get_kanji()
    vocab = vocabq.get_vocab()
    kset = set(q.literal for q in kanji)
    vkset = set(q.head for q in vocab if isinstance(q, vocabq.VocabKtoSQuestion))
    vrset = set(q.head for q in vocab if isinstance(q, vocabq.VocabRtoSQuestion))
    vr2set = set()
    for q in vocab:
        if isinstance(q, vocabq.VocabKtoRQuestion): vr2set.update(q.verifier.values)
    headset = set.union(kset, vkset, vrset)
    bothset = set.union(headset, vr2set)
    headlist = [r for r in records if r.word in headset]
    noheadlist = [r for r in records if r.word not in headset]
    r2list = [r for r in records if r.word not in headset and r.word in bothset]
    bothlist = [r for r in records if r.word in bothset]
    nolist = [r for r in records if r.word not in bothset]
    d = {}
    for r in records:
        d[r.word] = r.count
    orderedvocab = sorted(vocab, key=lambda q: d.get(q.head, 0), reverse=True)
    simplevocab = [q for q in orderedvocab if len(q.entries) == 1]
    complexvocab = [q for q in orderedvocab if len(q.entries) > 1]

