import xml.etree.cElementTree as xml
from question_basics import (
    CategoryQuestion, SimpleLeafQuestion, uid,
    SimpleVerifier, EnglishVerifier, UnsatisfiableError
    )

class KanjiToEnglishQuestion(SimpleLeafQuestion):
    def __init__(self, literal, answers,
                 jlpt=-1, grade=99,
                 freq=999999, stroke_count=None):
        super().__init__()
        self.literal = literal
        assert len(self.literal) == 1
        self.answers = answers
        self.verifier # check satisfiability
        self.jlpt = jlpt
        self.grade = grade
        self.freq = freq
        self.strokes = stroke_count
        assert self.strokes > 0

    @property
    def verifier(self):
        return EnglishVerifier(self.answers)

    @property
    def prompt(self):
        return "Kanji: What does %s mean?" % self.literal

    @property
    def body(self):
        return ("(Kanji) %s\n" % self.literal +
                "JLPT: %d, " % self.jlpt +
                "Grade: %d, " % self.grade +
                "Strokes: %d, " % self.strokes +
                "Freq: %d\n" % self.freq +
                "Meanings:\n" +
                "\n".join(self.answers))

    @property
    def q(self):
        return "kanji%d" % ord(self.literal)

    @classmethod
    def from_xml(cls, element):
        literal = element.find("literal").text
        reading_meaning = element.find("reading_meaning")
        if reading_meaning is None:
            raise UnsatisfiableError("No reading_meaning tag", element)
        answers = sum([[m.text
                        for m in rmgroup.findall("meaning")
                        if m.get("m_lang", "en") == "en"]
                       for rmgroup in reading_meaning.findall("rmgroup")],
                      [])
        misc = element.find("misc")
        kwargs = {}
        for tag in ['jlpt', 'grade', 'freq']:
            node = misc.find(tag)
            if node is not None:
                kwargs[tag] = int(node.text)
        kwargs['stroke_count'] = int(misc.find("stroke_count").text)
        return cls(literal, answers, **kwargs)

def get_kanji():
    kanjiRoot = xml.parse("../BigDataFiles/kanjidic2.xml").getroot()
    unsatisfiable = 0
    ordered = []
    for element in kanjiRoot.iterfind("character"):
        try:
            q = KanjiToEnglishQuestion.from_xml(element)
        except UnsatisfiableError:
            unsatisfiable += 1
            continue
        question = KanjiToEnglishQuestion.from_xml(element)
        ordered.append(question)
    print("Unsatisfiable:", unsatisfiable)
    return ordered
