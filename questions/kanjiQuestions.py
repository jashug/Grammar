import xml.etree.cElementTree as xml

def uord(c):
    if len(c) == 1:
        return ord(c)
    else:
        assert len(c) == 2
        assert 0xd800 <= ord(c[0]) <= 0xdbff
        assert 0xdc00 <= ord(c[1]) <= 0xdfff
        return 0x10000 + ((ord(c[0]) & 0x3FF) << 10) + (ord(c[1]) & 0x3FF)

def ulen(s):
    count = 0
    for i in range(len(s)):
        if 0xd800 <= ord(s[i]) <= 0xdbff:
            assert i + 1 < len(s)
            assert 0xdc00 <= ord(s[i+1]) <= 0xdfff
        elif 0xdc00 <= ord(s[i]) <= 0xdbff:
            assert i > 0
            assert 0xd800 <= ord(s[i]) <= 0xdbff
            count += 1
        else:
            count += 1
    return count

class KanjiToEnglishQuestion(object):
    def __init__(self, element):
        self.literal = element.find("literal").text
        reading_meaning = element.find("reading_meaning")
        self.answers = sum([[m.text.lower().strip()
                             for m in rmgroup.findall("meaning")
                             if m.get("m_lang", "en") == "en"]
                            for rmgroup in reading_meaning.findall("rmgroup")],
                           [])
        assert len(self.answers) > 0
        misc = element.find("misc")
        self.jlpt = self.defaultIntHelper(misc, 'jlpt', -1)
        self.grade = self.defaultIntHelper(misc, 'grade', 99)
        self.freq = self.defaultIntHelper(misc, 'freq', 999999)
        self.strokes = int(misc.find("stroke_count").text)

    def ask(self):
        print("(Kanji) What does %s mean?"%self.literal)

    def check(self, answer):
        return answer.lower().strip() in self.answers

    def body(self):
        print("(Kanji) %s"%self.literal)
        print(("JLPT: %(jlpt)d, Grade: %(grade)d, " +
               "Strokes: %(strokes)d, Freq: %(freq)d")%{
            'jlpt':self.jlpt, 'grade':self.grade, 'freq':self.freq,
            'strokes':self.strokes})
        print("Meanings:")
        for answer in self.answers:
            print(answer)

    @staticmethod
    def defaultIntHelper(misc, tag, default):
        node = misc.find(tag)
        return default if node is None else int(node.text)

def addKanjiToEnglish(qs):
    kanjiRoot = xml.parse("../BigDataFiles/kanjidic2.xml").getroot()
    rank = {}
    missingRM = 0
    missingMeaning = 0
    ordered = []
    for element in kanjiRoot.iterfind("character"):
        if element.find("reading_meaning") is None:
            missingRM += 1
            continue
        reading_meaning = element.find("reading_meaning")
        if len(sum([[m.text.lower().strip()
                     for m in rmgroup.findall("meaning")
                     if m.get("m_lang", "en") == "en"]
                    for rmgroup in reading_meaning.findall("rmgroup")],
                   [])) == 0:
            missingMeaning += 1
            continue
        q = KanjiToEnglishQuestion(element)
        #if ulen(q.literal) != 1: print "'%s'"%q.literal, len(q.literal)
        assert ulen(q.literal) == 1
        tag = "kanji%d"%uord(q.literal)
        assert tag not in qs
        qs[tag] = q
        rank[tag] = (q.grade, -q.jlpt, q.strokes, q.freq)
        ordered.append(tag)
    ordered.sort(key=lambda tag:rank[tag])
    return ordered

def addJLPTKanjiToEnglish(qs):
    ordered = addKanjiToEnglish(qs)
    return [q for q in ordered if qs[q].grade <= 8]
