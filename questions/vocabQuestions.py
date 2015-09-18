import xml.etree.ElementTree as xml
from collections import defaultdict, namedtuple
import base64
import pickle as pickle
from question_basics import (
    CategoryQuestion, SimpleLeafQuestion, uid,
    SimpleVerifier, EnglishVerifier, UnsatisfiableError
    )

class VocabRtoSQuestion(SimpleLeafQuestion):
    def __init__(self, read, pairs):
        super().__init__()
        self.read = read
        answers = set()
        for pair in pairs:
            answers.update(pair.sense.glosses)
        self.verifier = EnglishVerifier(answers)
        self.entries = defaultdict(list)
        for sreb, sense in pairs:
            assert sreb.reb == self.read
            if sense not in self.entries[sreb]:
                self.entries[sreb].append(sense)

    @property
    def prompt(self):
        return "VocabRtoS: What does %s mean?" % self.read

    @property
    def body(self):
        return ("(VocabRtoS) %s\n" % self.read +
                '\n'.join("Entry [%s]:\n" % ', '.join(sreb.pris) +
                          ''.join("Info: \n" + info for info in sreb.infos) +
                          ''.join(sense.body for sense in senses)
                          for sreb, senses in self.entries.items()) +
                "Meanings: %s\n" % '; '.join(self.verifier.values))

    @property
    def q(self):
        return "vocabRS%s"%uid(self.read)

class VocabKtoSQuestion(SimpleLeafQuestion):
    def __init__(self, kanji, tris):
        super().__init__()
        self.kanji = kanji
        answers = set()
        for tri in tris:
            answers.update(tri.sense.glosses)
        self.verifier = EnglishVerifier(answers)
        self.entries = defaultdict(list)
        for tri in tris:
            assert tri.keb.keb == self.kanji
            if tri.sense not in self.entries[tri.keb]:
                self.entries[tri.keb].append(tri.sense)

    @property
    def q(self):
        return "vocabKS.%s" % uid(self.kanji)

    @property
    def prompt(self):
        return "VocabKtoS: What does %s mean?" % self.kanji

    @property
    def body(self):
        return ("(VocabKtoS) %s\n" % self.kanji +
                '\n'.join("Entry [%s]:\n" % ', '.join(keb.pris) +
                          ''.join("Info: \n" + info for info in keb.infos) +
                          ''.join(sense.body for sense in senses)
                          for keb, senses in self.entries.items()) +
                "Meanings: %s\n" % '; '.join(self.verifier.values))

class VocabKtoRQuestion(SimpleLeafQuestion):
    def __init__(self, kanji, tris):
        super().__init__()
        self.kanji = kanji
        answers = set(tri.reb.reb for tri in tris)
        self.verifier = SimpleVerifier(answers)
        self.entries = defaultdict(list)
        for tri in tris:
            assert tri.keb.keb == self.kanji
            if tri.reb not in self.entries[tri.keb]:
                self.entries[tri.keb].append(tri.reb)

    @property
    def q(self):
        return "vocabKR.%s" % uid(self.kanji)

    @property
    def prompt(self):
        return "VocabKtoR: How is %s read?" % self.kanji

    @property
    def body(self):
        return ("(VocabKtoR) %s\n" % self.kanji +
                '\n'.join("Entry [%s]:\n" % ', '.join(keb.pris) +
                          ''.join("Info: %s\n" % info for info in keb.infos) +
                          ''.join("Reading: %s " % reb.reb +
                                  '[%s]\n' % ', '.join(reb.pris) +
                                  ''.join("Info: %s\n" % info
                                          for info in reb.infos)
                                  for reb in rebs)
                          for keb, rebs in self.entries.items()) +
                "Readings: %s\n" % '; '.join(self.verifier.values))

class KanjiElement(namedtuple("KanjiElement", ["keb", "infos", "pris"])):
    __slots__ = ()

    @classmethod
    def from_xml(cls, element):
        return cls(element.find("keb").text,
                   tuple(inf.text for inf in element.findall("ke_inf")),
                   tuple(pri.text for pri in element.findall("ke_pri")))

class ReadingElement(namedtuple("ReadingElement", ["reb", "infos", "pris",
                                                   "restrs", "nokanji"])):
    __slots__ = ()

    @classmethod
    def from_xml(cls, element):
        return cls(element.find("reb").text,
                   tuple(inf.text for inf in element.findall("re_inf")),
                   tuple(pri.text for pri in element.findall("re_pri")),
                   tuple(restr.text for restr in element.findall("re_restr")),
                   element.find("re_nokanji") is not None)

class Sense(namedtuple("Sense", ["glosses", "infos", "miscs", "fields",
                                 "stagks", "stagrs", "poss"])):
    __slots__ = ()

    @property
    def body(self):
        return ("Sense:\n" +
                ''.join("Part of Speech: %s\n" % pos for pos in self.poss) +
                ''.join("Info: %s\n" % info for info in self.infos) +
                ''.join("Misc: %s\n" % misc for misc in self.miscs) +
                ''.join("Field: %s\n" % field for field in self.fields) +
                ''.join("Applies to: %s\n" % restr for restr in self.stagks) +
                ''.join("Applies to: %s\n" % restr for restr in self.stagrs) +
                ''.join("Gloss: %s\n" % gloss for gloss in self.glosses))
    
    @classmethod
    def from_xml(cls, element, poss=None):
        poss = [pos.text for pos in element.findall("pos")] or poss
        assert poss
        assert element.find("gloss") is not None
        return cls([gloss.text for gloss in element.findall("gloss")],
                   [inf.text for inf in element.findall("s_inf")],
                   [misc.text for misc in element.findall("misc")],
                   [field.text for field in element.findall("field")],
                   [stagk.text for stagk in element.findall("stagk")],
                   [stagr.text for stagr in element.findall("stagr")],
                   poss), poss

    @classmethod
    def from_xml_collection(cls, elements):
        poss = None
        senses = []
        for element in elements:
            sense, poss = cls.from_xml(element, poss)
            senses.append(sense)
        return senses

Pair = namedtuple("Pair", ["sreb", "sense"])
Triple = namedtuple("Triple", ["keb", "reb", "sense"])

def parse_vocab():
    Reading = namedtuple("Reading", ["keb", "reb"])
    dictRoot = xml.parse("../BigDataFiles/JMdict_e.xml").getroot()
    pairs = []
    triples = []
    for e in dictRoot.iterfind("entry"):
        kebs = [KanjiElement.from_xml(k) for k in e.findall("k_ele")]
        # unique kebs
        kebset = set(keb.keb for keb in kebs)
        assert len(kebset) == len(kebs)

        rebs = [ReadingElement.from_xml(r) for r in e.findall("r_ele")]
        # unique rebs
        rebset = set(reb.reb for reb in rebs)
        assert len(rebset) == len(rebs)
        # valid restr fields
        assert all(not reb.nokanji or not reb.restrs for reb in rebs)
        assert set(sum((reb.restrs for reb in rebs), ())).issubset(kebset)

        assert e.find("sense") is not None
        assert e.find("sense").find("pos") is not None
        senses = Sense.from_xml_collection(e.findall("sense"))
        # valid restr fields
        assert set(sum((sense.stagks
                        for sense in senses), [])).issubset(kebset)
        assert set(sum((sense.stagrs
                        for sense in senses), [])).issubset(rebset)

        singleReadings = [reb for reb in rebs if reb.nokanji or not kebs]
        readings = []
        for reb in rebs:
            for keb in kebs:
                if keb.keb not in reb.restrs and not reb.nokanji:
                    readings.append(Reading(keb,reb))

        for sense in senses:
            for sreb in singleReadings:
                if ((not sense.stagks and not sense.stagrs) or
                    sreb.reb in sense.stagrs):
                    # This sense applies to the reb
                    pairs.append(Pair(sreb, sense))
        for sense in senses:
            for reading in readings:
                if ((not sense.stagks or reading.keb.keb in sense.stagks) and
                    (not sense.stagrs or reading.reb.reb in sense.stagrs)):
                    triples.append(Triple(reading.keb, reading.reb, sense))
    return pairs, triples

def make_questions(pairs, triples):
    rPairs = defaultdict(list)
    for pair in pairs:
        rPairs[pair.sreb.reb].append(pair)
    kTris = defaultdict(list)
    for tri in triples:
        kTris[tri.keb.keb].append(tri)

##    # equivalent to (nf, news, ichi, spec, gai)
##    priDesc = [('gai%d', 3), ('spec%d', 3), ('ichi%d', 3),
##               ('news%d', 3), ('nf%02d', 49)]
##    priMap = {}
##    placeValue = 1
##    for pref, num in priDesc:
##        for i in range(1, num):
##            priMap[pref%i] = placeValue * (num - i)
##        placeValue *= num

    questions = []
    for reb, pairs in rPairs.items():
        questions.append(VocabRtoSQuestion(reb, pairs))
    for keb, tris in kTris.items():
        questions.append(VocabKtoSQuestion(keb, tris))
        questions.append(VocabKtoRQuestion(keb, tris))
    return questions

def get_vocab():
    pairs, triples = parse_vocab()
    pairs = [pair for pair in pairs if pair.sreb.pris]
    triples = [tri for tri in triples if tri.keb.pris and tri.reb.pris]
    return make_questions(pairs, triples)
