import os.path
import unicodedata
import xml.etree.cElementTree as xml
from question_basics import (
    CategoryQuestion, SimpleLeafQuestion, uid,
    SimpleVerifier, EnglishVerifier, UnsatisfiableError
    )

class KanaQuestion(SimpleLeafQuestion):
    def __init__(self, kana, spellings):
        super().__init__()
        self.kana = kana
        assert len(self.kana) == 1
        self.verifier = EnglishVerifier(spellings)

    @property
    def prompt(self):
        return "Kana: Spell %s." % self.kana

    @property
    def body(self):
        return ("(Kana) %s\n" % self.kana +
                "%s\n" % unicodedata.name(self.kana).title() +
                "Spelled: %s\n" % '; '.join(self.verifier.values))

    @property
    def q(self):
        return "kana%d" % ord(self.kana)

class YoonQuestion(SimpleLeafQuestion):
    def __init__(self, yoon, spellings):
        super().__init__()
        self.yoon = yoon
        assert len(self.yoon) == 2
        self.verifier = EnglishVerifier(spellings)

    @property
    def prompt(self):
        return "Kana: Spell %s." % self.yoon

    @property
    def body(self):
        return ("(Yoon) %s\n" % self.yoon +
                "Spelled: %s\n" % '; '.join(self.verifier.values))

    @property
    def q(self):
        return "yoon%d.%d" % (ord(self.yoon[0]), ord(self.yoon[1]))

class DoubledConsonantQuestion(CategoryQuestion):
    prompt = "Kana: What is っ?"
    verifier = EnglishVerifier(["double consonant",])
    body = ("(Kana) っ\n" +
            "Double the following consonant. ずっと(zutto)\n" +
            "Meanings: %s\n" % '; '.join(verifier.values))
    q = "kana%d" % ord('っ')

kana = [
    ('あ', 'ア', ('a',)),
    ('い', 'イ', ('i',)),
    ('う', 'ウ', ('u',)),
    ('え', 'エ', ('e',)),
    ('お', 'オ', ('o',)),
    ('か', 'カ', ('ka',)),
    ('き', 'キ', ('ki',)),
    ('く', 'ク', ('ku',)),
    ('け', 'ケ', ('ke',)),
    ('こ', 'コ', ('ko',)),
    ('さ', 'サ', ('sa',)),
    ('し', 'シ', ('si', 'shi',)),
    ('す', 'ス', ('su',)),
    ('せ', 'セ', ('se',)),
    ('そ', 'ソ', ('so',)),
    ('た', 'タ', ('ta',)),
    ('ち', 'チ', ('ti', 'chi',)),
    ('つ', 'ツ', ('tu', 'tsu',)),
    ('て', 'テ', ('te',)),
    ('と', 'ト', ('to',)),
    ('な', 'ナ', ('na',)),
    ('に', 'ニ', ('ni',)),
    ('ぬ', 'ヌ', ('nu',)),
    ('ね', 'ネ', ('ne',)),
    ('の', 'ノ', ('no',)),
    ('は', 'ハ', ('ha',)),
    ('ひ', 'ヒ', ('hi',)),
    ('ふ', 'フ', ('hu', 'fu')),
    ('へ', 'ヘ', ('he',)),
    ('ほ', 'ホ', ('ho',)),
    ('ま', 'マ', ('ma',)),
    ('み', 'ミ', ('mi',)),
    ('む', 'ム', ('mu',)),
    ('め', 'メ', ('me',)),
    ('も', 'モ', ('mo',)),
    ('や', 'ヤ', ('ya',)),
    ('ゆ', 'ユ', ('yu',)),
    ('よ', 'ヨ', ('yo',)),
    ('ら', 'ラ', ('ra',)),
    ('り', 'リ', ('ri',)),
    ('る', 'ル', ('ru',)),
    ('れ', 'レ', ('re',)),
    ('ろ', 'ロ', ('ro',)),
    ('わ', 'ワ', ('wa',)),
    ('を', 'ヲ', ('wo',)),
    ('ん', 'ン', ('nn',)),
    ('が', 'ガ', ('ga',)),
    ('ぎ', 'ギ', ('gi',)),
    ('ぐ', 'グ', ('gu',)),
    ('げ', 'ゲ', ('ge',)),
    ('ご', 'ゴ', ('go',)),
    ('ざ', 'ザ', ('za',)),
    ('じ', 'ジ', ('zi', 'ji',)),
    ('ず', 'ズ', ('zu',)),
    ('ぜ', 'ゼ', ('ze',)),
    ('ぞ', 'ゾ', ('zo',)),
    ('だ', 'ダ', ('da',)),
    ('ぢ', 'ヂ', ('di',)),
    ('づ', 'ヅ', ('du',)),
    ('で', 'デ', ('de',)),
    ('ど', 'ド', ('do',)),
    ('ば', 'バ', ('ba',)),
    ('び', 'ビ', ('bi',)),
    ('ぶ', 'ブ', ('bu',)),
    ('べ', 'ベ', ('be',)),
    ('ぼ', 'ボ', ('bo',)),
    ('ぱ', 'パ', ('pa',)),
    ('ぴ', 'ピ', ('pi',)),
    ('ぷ', 'プ', ('pu',)),
    ('ぺ', 'ペ', ('pe',)),
    ('ぽ', 'ポ', ('po',)),
]

yoon = [
    ('きゃ', 'キャ', ('kya',)),
    ('しゃ', 'シャ', ('sya', 'sha',)),
    ('ちゃ', 'チャ', ('cya', 'cha',)),
    ('にゃ', 'ニャ', ('nya',)),
    ('ひゃ', 'ヒャ', ('hya',)),
    ('みゃ', 'ミャ', ('mya',)),
    ('りゃ', 'リャ', ('rya',)),
    ('ぎゃ', 'ギャ', ('gya',)),
    ('じゃ', 'ジャ', ('jya',)),
    ('びゃ', 'ビャ', ('bya',)),
    ('ぴゃ', 'ピャ', ('pya',)),
    ('きゅ', 'キュ', ('kyu',)),
    ('しゅ', 'シュ', ('syu', 'shu',)),
    ('ちゅ', 'チュ', ('cyu', 'chu',)),
    ('にゅ', 'ニュ', ('nyu',)),
    ('ひゅ', 'ヒュ', ('hyu',)),
    ('みゅ', 'ミュ', ('myu',)),
    ('りゅ', 'リュ', ('ryu',)),
    ('ぎゅ', 'ギュ', ('gyu',)),
    ('じゅ', 'ジュ', ('jyu',)),
    ('びゅ', 'ビュ', ('byu',)),
    ('ぴゅ', 'ピュ', ('pyu',)),
    ('きょ', 'キョ', ('kyo',)),
    ('しょ', 'ショ', ('syo', 'sho',)),
    ('ちょ', 'チョ', ('cyo', 'cho',)),
    ('にょ', 'ニョ', ('nyo',)),
    ('ひょ', 'ヒョ', ('byo',)),
    ('みょ', 'ミョ', ('myo',)),
    ('りょ', 'リョ', ('ryo',)),
    ('ぎょ', 'ギョ', ('gyo',)),
    ('じょ', 'ジョ', ('jyo',)),
    ('びょ', 'ビョ', ('byo',)),
    ('ぴょ', 'ピョ', ('pyo',)),
]

def get_kana():
    questions = []
    for hiragana, katakana, spellings in kana:
        questions.append(KanaQuestion(hiragana, spellings))
        questions.append(KanaQuestion(katakana, spellings))
    for hiragana, katakana, spellings in yoon:
        questions.append(YoonQuestion(hiragana, spellings))
        questions.append(YoonQuestion(katakana, spellings))
    questions.append(DoubledConsonantQuestion)
    return questions

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
                "Meanings:\n%s\n" % "\n".join(self.answers))

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
    path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'BigDataFiles', 'kanjidic2.xml')
    kanjiRoot = xml.parse(path).getroot()
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
    #print("Unsatisfiable:", unsatisfiable)
    return ordered
