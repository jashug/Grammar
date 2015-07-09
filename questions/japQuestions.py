from collections import defaultdict

import kanjiQuestions, vocabQuestions
from vocabQuestions import VocabRtoSQuestion
from vocabQuestions import VocabKtoSQuestion, VocabKtoRQuestion
from vocabQuestions import VocabKRtoSQuestion, VocabKStoRQuestion

def getPriNF(q):
    if isinstance(q, VocabRtoSQuestion):
        pris = sum((sreb[2] for sreb, senses in q.entries), [])
    elif isinstance(q, VocabKtoSQuestion):
        pris = sum((keb[2] for keb, senses in q.entries), [])
    elif isinstance(q, VocabKtoRQuestion):
        pris = sum((keb[2] for keb, rebs in q.entries), [])
    elif isinstance(q, VocabKRtoSQuestion):
        pris = sum((keb[2] for (keb, reb), senses in q.entries), [])
    elif isinstance(q, VocabKStoRQuestion):
        pris = sum((keb[2] for (keb, sense), rebs in q.entries), [])
    else:
        raise Exception("Unknown Question Type: %s"%str(type(q)))
    return min(int(pri[2:]) if pri[:2] == "nf" else 49 for pri in pris)

def getKeb(q):
    return q.read if isinstance(q, VocabRtoSQuestion) else q.kanji

def kanjiSet(keb):
    out = []
    for c in keb:
        if 0xdc00 <= ord(c) <= 0xdfff:
            out[-1] += c
        elif not (0xff01 <= ord(c) <= 0xff5e or
                  0x3040 <= ord(c) <= 0x30ff or
                  ord(c) == 0x3005):
            out.append(c)
    return out

def addJapaneseQuestions(qs, vocabCache=None):
    orderedKanji = kanjiQuestions.addKanjiToEnglish(qs)
    if vocabCache is None:
        raise Exception("Need Cache")
    else:
        orderedVocab = vocabQuestions.addVocabSetShortcut(vocabCache, qs)

    #print "Obtained sources"

    # generate chunk data for kanji
    chunk = defaultdict(lambda :49)
    for q in orderedVocab:
        question = qs[q]
        pri = getPriNF(question)
        for kanji in kanjiSet(getKeb(question)):
            if pri < chunk[kanji]: chunk[kanji] = pri

    # generate rank data (chunk, kanjiI, vocabI)
    rank = {}
    ordered = []
    kanjiIndex = {}
    for i in range(len(orderedKanji)):
        q = orderedKanji[i]
        question = qs[q]
        assert question.literal not in kanjiIndex
        kanjiIndex[question.literal] = i
        assert q not in rank
        rank[q] = (chunk[question.literal], i, len(question.literal), -1)
        ordered.append(q)

    #global missing
    #missing = set()
    #for q in orderedVocab:
    #    for kanji in kanjiSet(getKeb(qs[q])):
    #        if kanji not in kanjiIndex:
    #            missing.add(kanji)
    #if missing: print ''.join(sorted(missing))
    #assert len(missing) == 0
    
    for i in range(len(orderedVocab)):
        q = orderedVocab[i]
        question = qs[q]
        keb = getKeb(question)
        # normalize kanji / 1 char vocab (remove 1 char vocab)
        if isinstance(question, VocabKtoSQuestion) and keb in kanjiIndex:
            ques2 = qs[orderedKanji[kanjiIndex[keb]]]
            ques2.answers += list(question.answers-set(ques2.answers))
            question.answers.update(ques2.answers)
            del qs[q]
            continue
        assert q not in rank
        rank[q] = (getPriNF(question),
                   max(-1,-1, *(kanjiIndex[kanji] for kanji in kanjiSet(keb))),
                   len(keb),
                   i)
        ordered.append(q)

##    tot = 0
##    for i in range(1, 50):
##        ks = [k for k in chunk if chunk[k] == i]# and kanjiIndex[k] >= 1006]
##        vqs = [vq for vq in orderedVocab if vq in rank and rank[vq][0] == i]
##        ks.sort(key = lambda k:kanjiIndex[k])
##        vqs.sort(key = lambda vq:rank[vq])
##        print "Chunk %d:"%i
##        print "Kanji: %d"%len(ks)
##        print "Vocab Questions: %d"%len(vqs)
##        tot += len(ks) + len(vqs)
##        print "Total: %d"%tot
##        #print ''.join(ks)
        

    return (sorted(ordered, key=lambda q:rank[q]),
            [q for q in orderedKanji if q in qs],
            [q for q in orderedVocab if q in qs],
            [[q for q in rank if rank[q][0] == i] for i in range(50)])
