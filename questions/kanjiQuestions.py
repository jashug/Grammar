import os.path
import unicodedata
import xml.etree.cElementTree as xml
from question_basics import (
    CategoryQuestion, SimpleLeafQuestion, uid,
    SimpleVerifier, EnglishVerifier, Literal, UnsatisfiableError
    )

class KanaQuestion(SimpleLeafQuestion):
    explanation = ""
    def __init__(self, kana, spellings):
        super().__init__()
        self.head = kana
        assert len(kana) == 1
        self.verifier = Literal(spellings)

    @property
    def prompt(self):
        return "Kana: How is %s spelled?" % self.head

    @property
    def body(self):
        return ("(Kana) %s\n" % self.head +
                "%s\n" % unicodedata.name(self.head).title() +
                self.explanation +
                "Spelled: %s" % '; '.join(self.verifier.values))

    @property
    def q(self):
        return "kana%d" % ord(self.head)

class HiraganaYoonQuestion(KanaQuestion):
    example_heads = 'きし'
    def __init__(self, yoon, vowel):
        super().__init__(yoon, ['ly' + vowel, 'xy' + vowel])
        self.vowel = vowel

    @property
    def explanation(self):
        vowel = self.vowel
        return ("Little y kana form yoon by palatizing the sound.\n"
                "Example: %s can be spelled %s, %s, %s.\n" %
                (self.example_heads[0] + self.head,
                 'ky' + vowel, 'kily' + vowel, 'kixy' + vowel) +
                "Example: %s can be spelled %s, %s, %s, %s, %s, %s.\n" %
                (self.example_heads[1] + self.head,
                 'sh' + vowel, 'sy' + vowel, 'shily' + vowel,
                 'shixy' + vowel, 'sily' + vowel, 'sixy' + vowel))

class KatakanaYoonQuestion(HiraganaYoonQuestion):
    example_heads = 'キシ'

HiraganaLittleTsuQuestion = KanaQuestion('っ', ['ltsu', 'ltu', 'xtsu', 'xtu'])
HiraganaLittleTsuQuestion.explanation = """\
Doubles the following consonant,
bringing the sound to the end of the preceding mora.
Example: ずっと is spelled zutto.
"""
KatakanaLittleTsuQuestion = KanaQuestion('ッ', ['ltsu', 'ltu', 'xtsu', 'xtu'])
KatakanaLittleTsuQuestion.explanation = """\
Doubles the following consonant,
bringing the sound to the end of the preceding mora.
Example: ズット is spelled zutto.
"""

LongVowelQuestion = KanaQuestion('ー', ['-',])
LongVowelQuestion.explanation = """\
Make the previous vowel long.
Ususally only Katakana.
Hiragana usually extends the vowel with あいう(えお)
Example: nannbaa(number) could be written ナンバー or なんばあ.
"""

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
    ('ゃ', 'ャ', 'a'),
    ('ゅ', 'ュ', 'u'),
    ('ょ', 'ョ', 'o'),
]

def iterate_with_yoon(s):
    return iter(s)

def get_kana():
    questions = []
    for hiragana, katakana, spellings in kana:
        questions.append(KanaQuestion(hiragana, spellings))
        questions.append(KanaQuestion(katakana, spellings))
    for hiragana, katakana, vowel in yoon:
        questions.append(HiraganaYoonQuestion(hiragana, vowel))
        questions.append(KatakanaYoonQuestion(katakana, vowel))
    questions.append(HiraganaLittleTsuQuestion)
    questions.append(KatakanaLittleTsuQuestion)
    questions.append(LongVowelQuestion)
    return questions

class KanjiToEnglishQuestion(SimpleLeafQuestion):
    def __init__(self, literal, answers,
                 jlpt=-1, grade=99,
                 freq=999999, stroke_count=None):
        super().__init__()
        self.head = literal
        assert len(literal) == 1
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
        return "Kanji: What does %s mean?" % self.head

    @property
    def body(self):
        return ("(Kanji) %s\n" % self.head +
                "JLPT: %d, " % self.jlpt +
                "Grade: %d, " % self.grade +
                "Strokes: %d, " % self.strokes +
                "Freq: %d\n" % self.freq +
                "Meanings:\n%s" % "\n".join(self.answers))

    @property
    def q(self):
        return "kanji%d" % ord(self.head)

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

class RepetitionMarkQuestion(CategoryQuestion):
    head = '々'
    prompt = "Kanji: What does %s mean?" % head
    verifier = EnglishVerifier(["repeated kanji",])
    body = ("(Kanji) %s\n" % head +
            "Repeat the previous kanji (sometimes voiced).\n" +
            "Example: 人々　is read ひとびと\n" +
            "Meanings:\n%s" % '\n'.join(verifier.values))
    q = "kanji%d" % ord(head)
    parts = [verifier,]

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
    ordered.append(RepetitionMarkQuestion)
    #print("Unsatisfiable:", unsatisfiable)
    return ordered
