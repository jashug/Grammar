import xml.etree.cElementTree as xml
from collections import defaultdict
import base64
import cPickle as pickle

def uid(s):
    """Generate a unique ASCII string for a unicode string."""
    return base64.urlsafe_b64encode(s.encode("UTF-8"))

def regSpace(s):
    out = [[]]
    for c in s:
        if c == ' ': out.append([])
        else: out[-1].append(c)
    return ' '.join(''.join(word) for word in out if word)

def elimParens(s):
    """Remove parenthesized portions of s."""
    out = []
    i = 0
    for c in s:
        if c == '(': i += 1
        elif c == ')': i -= 1
        elif i == 0: out.append(c)
        if i < 0: raise Exception("Unbalenced parens: %s"%s)
    if i != 0: raise Exception("Unbalenced parens: %s"%s)
    return regSpace(''.join(out))

class VocabRtoSQuestion(object):
    def __init__(self, read, pairs):
        self.read = read
        self.key = "vocabRS%s"%uid(read)
        self.answers = set()
        for pair in pairs:
            self.answers.update(set(elimParens(gloss).lower().strip()
                                    for gloss in pair[1][0]))
        self.entries = []
        for sreb, sense in pairs:
            for entry in self.entries:
                if entry[0] == sreb:
                    if sense not in entry[1]: entry[1].append(sense)
                    break
            else:
                self.entries.append((sreb, [sense,]))

    def ask(self):
        print "(VocabRtoS) What does %s mean?"%self.read

    def check(self, answer):
        return answer.lower().strip() in self.answers

    def body(self):
        print "(VocabRtoS) %s"%self.read
        for sreb, senses in self.entries:
            print "Entry [" + ', '.join(sreb[2]) + ']:'
            for info in sreb[1]:
                print "Info: " + info
            for sense in senses:
                print "Sense:"
                for pos in sense[6]:
                    print "Part of Speech: " + pos
                for info in sense[1]:
                    print "Info: " + info
                for misc in sense[2]:
                    print "Misc: " + misc
                for field in sense[3]:
                    print "Field: " + field
                for gloss in sense[0]:
                    print "Gloss: " + gloss
        print "Meanings: " + '; '.join(self.answers)

class VocabKtoSQuestion(object):
    def __init__(self, kanji, tris):
        self.kanji = kanji
        self.key = "vocabKS.%s"%uid(kanji)
        self.answers = set()
        for tri in tris:
            self.answers.update(set(elimParens(gloss).lower().strip()
                                    for gloss in tri[2][0]))
        self.entries = []
        for keb, reb, sense in tris:
            for entry in self.entries:
                if entry[0] == keb:
                    if sense not in entry[1]: entry[1].append(sense)
                    break
            else:
                self.entries.append((keb, [sense,]))

    def ask(self):
        print "(VocabKtoS) What does %s mean?" % self.kanji

    def check(self, answer):
        return answer.lower().strip() in self.answers

    def body(self):
        print "(VocabKtoS) %s" % self.kanji
        for keb, senses in self.entries:
            print "Entry [" + ', '.join(keb[2]) + ']:'
            for info in keb[1]:
                print "Info: " + info
            for sense in senses:
                print "Sense:"
                for pos in sense[6]:
                    print "Part of Speech: " + pos
                for info in sense[1]:
                    print "Info: " + info
                for misc in sense[2]:
                    print "Misc: " + misc
                for field in sense[3]:
                    print "Field: " + field
                for gloss in sense[0]:
                    print "Gloss: " + gloss
        print "Meanings: " + '; '.join(self.answers)

class VocabKtoRQuestion(object):
    def __init__(self, kanji, tris):
        self.kanji = kanji
        self.key = "vocabKR.%s"%uid(kanji)
        self.answers = set(tri[1][0] for tri in tris)
        self.entries = []
        for keb, reb, sense in tris:
            for entry in self.entries:
                if entry[0] == keb:
                    if reb not in entry[1]: entry[1].append(reb)
                    break
            else:
                self.entries.append((keb, [reb,]))

    def ask(self):
        print "(VocabKtoR) How is %s read?" % self.kanji

    def check(self, answer):
        return answer in self.answers

    def body(self):
        print "(VocabKtoR) %s" % self.kanji
        for keb, rebs in self.entries:
            print "Entry [" + ', '.join(keb[2]) + ']:'
            for info in keb[1]:
                print "Info: " + info
            for reb in rebs:
                print "Reading: %s [%s]" % (reb[0], ', '.join(reb[2]))
                for info in reb[1]:
                    print "Info: " + info
        print "Readings: " + '; '.join(self.answers)

class VocabKRtoSQuestion(object):
    def __init__(self, kanji, read, tris):
        self.kanji = kanji
        self.read = read
        self.key = "vocabKRS%s.%s"%(uid(kanji), uid(read))
        self.answers = set()
        for tri in tris:
            self.answers.update(set(elimParens(gloss).lower().strip()
                                    for gloss in tri[2][0]))
        self.entries = []
        for keb, reb, sense in tris:
            for entry in self.entries:
                if entry[0] == (keb, reb):
                    if sense not in entry[1]: entry[1].append(sense)
                    break
            else:
                self.entries.append(((keb, reb), [sense,]))

    def ask(self):
        print ("(VocabKRtoS) What does %s mean when read %s?" %
               (self.kanji, self.read))

    def check(self, answer):
        return answer.lower().strip() in self.answers

    def body(self):
        print "(VocabKRtoS) %s as %s" % (self.kanji, self.read)
        for (keb, reb), senses in self.entries:
            print "Entry:"
            print "Keb [" + ', '.join(keb[2]) + ']:'
            for info in keb[1]:
                print "Info: " + info
            print "Reb [" + ', '.join(reb[2]) + ']:'
            for info in reb[1]:
                print "Info: " + info
            for sense in senses:
                print "Sense:"
                for pos in sense[6]:
                    print "Part of Speech: " + pos
                for info in sense[1]:
                    print "Info: " + info
                for misc in sense[2]:
                    print "Misc: " + misc
                for field in sense[3]:
                    print "Field: " + field
                for gloss in sense[0]:
                    print "Gloss: " + gloss
        print "Meanings: " + '; '.join(self.answers)

class VocabKStoRQuestion(object):
    def __init__(self, kanji, sens, tris):
        self.kanji = kanji
        self.sens = sens
        self.key = "vocabKSR%s.%s"%(uid(kanji), uid(sens))
        self.answers = set(tri[1][0] for tri in tris)
        self.entries = []
        for keb, reb, sense in tris:
            for entry in self.entries:
                if entry[0] == (keb, sense):
                    if reb not in entry[1]: entry[1].append(reb)
                    break
            else:
                self.entries.append(((keb, sense), [reb,]))

    def ask(self):
        print "(VocabKStoR) How is %s read in the sense of %s" % \
              (self.kanji, self.sens)

    def check(self, answer):
        return answer.lower().strip() in self.answers

    def body(self):
        print "(VocabKStoR) %s as %s" % (self.kanji, self.sens)
        for (keb, sense), rebs in self.entries:
            print "Entry [" + ', '.join(keb[2]) + ']:'
            for info in keb[1]:
                print "Info: " + info
            print "Sense:"
            for pos in sense[6]:
                print "Part of Speech: " + pos
            for info in sense[1]:
                print "Info: " + info
            for misc in sense[2]:
                print "Misc: " + misc
            for field in sense[3]:
                print "Field: " + field
            for reb in rebs:
                print "Reading: %s [%s]" % (reb[0], ', '.join(reb[2]))
                for info in reb[1]:
                    print "Info: " + info
        print "Readings: " + '; '.join(self.answers)

def addVocabSet(qs):
    dictRoot = xml.parse("../BigDataFiles/JMdict_e.xml").getroot()
    pairs = []
    triples = []
    for e in dictRoot.iterfind("entry"):
        kebs = [(k.find("keb").text,
                 [inf.text for inf in k.findall("ke_inf")],
                 [pri.text for pri in k.findall("ke_pri")])
                for k in e.findall("k_ele")]
        # unique kebs
        assert len(set(kanji for kanji,infs,pris in kebs)) == len(kebs)

        rebs = [(r.find("reb").text,
                 [inf.text for inf in r.findall("re_inf")],
                 [pri.text for pri in r.findall("re_pri")],
                 [restr.text for restr in r.findall("re_restr")],
                 r.find("re_nokanji") is not None)
                for r in e.findall("r_ele")]
        # unique rebs
        assert (len(set(read for read,infs,pris,restrs,nokanji in rebs)) ==
                len(rebs))
        # valid restr fields
        assert all(not nokanji or not restrs
                   for read,infs,pris,restrs,nokanji in rebs)
        assert all(all(any(kanji == restr for kanji,infs,pris in kebs)
                       for restr in restrs)
                   for read,infs,pris,restrs,nokanji in rebs)

        assert e.find("sense") is not None
        assert e.find("sense").find("pos") is not None
        senses = []
        for sense in e.findall("sense"):
            if sense.find("pos") is not None:
                currentPos = [pos.text for pos in sense.findall("pos")]
            senses.append(([gloss.text for gloss in sense.findall("gloss")],
                           [inf.text for inf in sense.findall("s_inf")],
                           [misc.text for misc in sense.findall("misc")],
                           [field.text for field in sense.findall("field")],
                           [stagk.text for stagk in sense.findall("stagk")],
                           [stagr.text for stagr in sense.findall("stagr")],
                           currentPos))
        # valid restr fields
        assert all(all(any(kanji == restr for kanji,infs,pris in kebs)
                       for restr in stagks) and
                   all(any(read == restr for read,infs,ps,rs,nk in rebs)
                       for restr in stagrs)
                   for gs,infs,ms,fs,stagks,stagrs,poss in senses)


        singleReadings = [reb for reb in rebs if reb[4] or not kebs] # nokanji
        readings = []
        for reb in rebs:
            for keb in kebs:
                if keb[0] not in reb[3] and not reb[4]:
                    readings.append((keb,reb))

        for sense in senses:
            for sreb in singleReadings:
                if (not sense[4] and not sense[5]) or sreb[0] in sense[5]:
                    pairs.append((sreb, sense))
        for sense in senses:
            for reading in readings:
                if ((not sense[4] or reading[0][0] in sense[4]) and
                    (not sense[5] or reading[1][0] in sense[5])):
                    triples.append((reading[0], reading[1], sense))

    #print "Generated pairs, triples"
    pairs = [pair for pair in pairs if len(pair[0][2]) > 0]
    triples = [tri for tri in triples
               if len(tri[0][2]) > 0 and len(tri[1][2]) > 0]
    #print "Filtered pairs, triples"
    
    rPairs = defaultdict(lambda :([],set()))
    for pair in pairs:
        rPairs[pair[0][0]][0].append(pair)
        rPairs[pair[0][0]][1].update(set(pair[1][0]))
    del pair
    kRTris = defaultdict(lambda :([],set()))
    kSTris = defaultdict(lambda :([],set()))
    krSTris = defaultdict(lambda :([],set()))
    ksRTris = defaultdict(lambda :([],set()))
    for tri in triples:
        kSTris[tri[0][0]][0].append(tri)
        kSTris[tri[0][0]][1].update(set(elimParens(x).lower().strip()
                                        for x in tri[2][0]))
        kRTris[tri[0][0]][0].append(tri)
        kRTris[tri[0][0]][1].add(tri[1][0])
        krSTris[(tri[0][0],tri[1][0])][0].append(tri)
        krSTris[(tri[0][0],tri[1][0])][1].update(
            set(elimParens(x).lower().strip() for x in tri[2][0]))
        ksRTris[(tri[0][0],'; '.join(elimParens(x).lower().strip()
                                     for x in tri[2][0]))][0].append(tri)
        ksRTris[(tri[0][0],'; '.join(elimParens(x).lower().strip()
                                     for x in tri[2][0]))][1].add(tri[1][0])
    del tri
    #print "Gathered terms"

    # equivalent to (nf, news, ichi, spec, gai)
    priDesc = [('gai%d', 3), ('spec%d', 3), ('ichi%d', 3),
               ('news%d', 3), ('nf%02d', 49)]
    priMap = {}
    placeValue = 1
    for pref, num in priDesc:
        for i in range(1, num):
            priMap[pref%i] = placeValue * (num - i)
        placeValue *= num

    #global rank
    rank = {}
    ordered = []
    for read in rPairs:
        q = VocabRtoSQuestion(read, rPairs[read][0])
        assert q.key not in qs
        qs[q.key] = q
        rank[q.key] = (-max(sum(priMap[pri] for pri in pair[0][2])
                            for pair in rPairs[read][0]),
                       read)
        ordered.append(q.key)
    for kanji in kSTris:
        q = VocabKtoSQuestion(kanji, kSTris[kanji][0])
        assert q.key not in qs
        qs[q.key] = q
        rank[q.key] = (-max(sum(priMap[pri] for pri in tri[0][2])
                            for tri in kSTris[kanji][0]),
                       kanji, 0)
        ordered.append(q.key)
    for kanji in kRTris:
        q = VocabKtoRQuestion(kanji, kRTris[kanji][0])
        assert q.key not in qs
        qs[q.key] = q
        rank[q.key] = (-max(sum(priMap[pri] for pri in tri[0][2])
                            for tri in kRTris[kanji][0]),
                       kanji, 1)
        ordered.append(q.key)
    for kanji, read in krSTris:
        if krSTris[(kanji, read)][1] != kSTris[kanji][1]:
            q = VocabKRtoSQuestion(kanji, read, krSTris[(kanji, read)][0])
            assert q.key not in qs
            qs[q.key] = q
            rank[q.key] = (-max(sum(priMap[pri] for pri in tri[0][2])
                                for tri in krSTris[(kanji, read)][0]),
                           kanji, 2,
                           -max(sum(priMap[pri] for pri in tri[1][2])
                                for tri in krSTris[(kanji, read)][0]),
                           read)
            ordered.append(q.key)
    for kanji, sense in ksRTris:
        if ksRTris[(kanji, sense)][1] != kRTris[kanji][1]:
            q = VocabKStoRQuestion(kanji, sense, ksRTris[(kanji, sense)][0])
            assert q.key not in qs
            qs[q.key] = q
            rank[q.key] = (-max(sum(priMap[pri] for pri in tri[0][2])
                                for tri in ksRTris[(kanji, sense)][0]),
                           kanji, 3,
                           -max(sum(priMap[pri] for pri in tri[1][2])
                                for tri in ksRTris[(kanji, sense)][0]),
                           sense)
            ordered.append(q.key)
    ordered.sort(key = lambda q:rank[q])
    return ordered

##def storeShortcut(path):
##    qs = {}
##    ordered = addVocabSet(qs)
##    with open(path, 'wb') as f:
##        pickle.dump((qs, ordered), f, 0)

def addVocabSetShortcut(path, qs):
    with open(path, 'rb') as f:
        qsSub, ordered = pickle.load(f)
    for key in qsSub:
        assert key not in qs
        qs[key] = qsSub[key]
    return ordered
