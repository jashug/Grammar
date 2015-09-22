# -*- coding: utf-8 -*-
import pickle as pickle
import os
import time
from pprint import pprint
from collections import defaultdict
import itertools, functools

#from questions.grammarQuestions import entities
#from questions import japQuestions as jap
from questions import vocabQuestions as voc
from question_basics import EnglishVerifier

entities = """\
<!ENTITY MA "martial arts term">
<!ENTITY X "rude or X-rated term (not displayed in educational software)">
<!ENTITY abbr "abbreviation">
<!ENTITY adj-i "adjective (keiyoushi)">
<!ENTITY adj-ix "adjective (keiyoushi) - yoi/ii class">
<!ENTITY adj-na "adjectival nouns or quasi-adjectives (keiyodoshi)">
<!ENTITY adj-no "nouns which may take the genitive case particle `no'">
<!ENTITY adj-pn "pre-noun adjectival (rentaishi)">
<!ENTITY adj-t "`taru' adjective">
<!ENTITY adj-f "noun or verb acting prenominally">
<!ENTITY adv "adverb (fukushi)">
<!ENTITY adv-to "adverb taking the `to' particle">
<!ENTITY arch "archaism">
<!ENTITY ateji "ateji (phonetic) reading">
<!ENTITY aux "auxiliary">
<!ENTITY aux-v "auxiliary verb">
<!ENTITY aux-adj "auxiliary adjective">
<!ENTITY Buddh "Buddhist term">
<!ENTITY chem "chemistry term">
<!ENTITY chn "children's language">
<!ENTITY col "colloquialism">
<!ENTITY comp "computer terminology">
<!ENTITY conj "conjunction">
<!ENTITY cop-da "copula">
<!ENTITY ctr "counter">
<!ENTITY derog "derogatory">
<!ENTITY eK "exclusively kanji">
<!ENTITY ek "exclusively kana">
<!ENTITY exp "expressions (phrases, clauses, etc.)">
<!ENTITY fam "familiar language">
<!ENTITY fem "female term or language">
<!ENTITY food "food term">
<!ENTITY geom "geometry term">
<!ENTITY gikun "gikun (meaning as reading) or jukujikun (special kanji reading)">
<!ENTITY hon "honorific or respectful (sonkeigo) language">
<!ENTITY hum "humble (kenjougo) language">
<!ENTITY iK "word containing irregular kanji usage">
<!ENTITY id "idiomatic expression">
<!ENTITY ik "word containing irregular kana usage">
<!ENTITY int "interjection (kandoushi)">
<!ENTITY io "irregular okurigana usage">
<!ENTITY iv "irregular verb">
<!ENTITY ling "linguistics terminology">
<!ENTITY m-sl "manga slang">
<!ENTITY male "male term or language">
<!ENTITY male-sl "male slang">
<!ENTITY math "mathematics">
<!ENTITY mil "military">
<!ENTITY n "noun (common) (futsuumeishi)">
<!ENTITY n-adv "adverbial noun (fukushitekimeishi)">
<!ENTITY n-suf "noun, used as a suffix">
<!ENTITY n-pref "noun, used as a prefix">
<!ENTITY n-t "noun (temporal) (jisoumeishi)">
<!ENTITY num "numeric">
<!ENTITY oK "word containing out-dated kanji">
<!ENTITY obs "obsolete term">
<!ENTITY obsc "obscure term">
<!ENTITY ok "out-dated or obsolete kana usage">
<!ENTITY oik "old or irregular kana form">
<!ENTITY on-mim "onomatopoeic or mimetic word">
<!ENTITY pn "pronoun">
<!ENTITY poet "poetical term">
<!ENTITY pol "polite (teineigo) language">
<!ENTITY pref "prefix">
<!ENTITY proverb "proverb">
<!ENTITY prt "particle">
<!ENTITY physics "physics terminology">
<!ENTITY rare "rare">
<!ENTITY sens "sensitive">
<!ENTITY sl "slang">
<!ENTITY suf "suffix">
<!ENTITY uK "word usually written using kanji alone">
<!ENTITY uk "word usually written using kana alone">
<!ENTITY unc "unclassified">
<!ENTITY yoji "yojijukugo">
<!ENTITY v1 "Ichidan verb">
<!ENTITY v1-s "Ichidan verb - kureru special class">
<!ENTITY v2a-s "Nidan verb with 'u' ending (archaic)">
<!ENTITY v4h "Yodan verb with `hu/fu' ending (archaic)">
<!ENTITY v4r "Yodan verb with `ru' ending (archaic)">
<!ENTITY v5aru "Godan verb - -aru special class">
<!ENTITY v5b "Godan verb with `bu' ending">
<!ENTITY v5g "Godan verb with `gu' ending">
<!ENTITY v5k "Godan verb with `ku' ending">
<!ENTITY v5k-s "Godan verb - Iku/Yuku special class">
<!ENTITY v5m "Godan verb with `mu' ending">
<!ENTITY v5n "Godan verb with `nu' ending">
<!ENTITY v5r "Godan verb with `ru' ending">
<!ENTITY v5r-i "Godan verb with `ru' ending (irregular verb)">
<!ENTITY v5s "Godan verb with `su' ending">
<!ENTITY v5t "Godan verb with `tsu' ending">
<!ENTITY v5u "Godan verb with `u' ending">
<!ENTITY v5u-s "Godan verb with `u' ending (special class)">
<!ENTITY v5uru "Godan verb - Uru old class verb (old form of Eru)">
<!ENTITY vz "Ichidan verb - zuru verb (alternative form of -jiru verbs)">
<!ENTITY vi "intransitive verb">
<!ENTITY vk "Kuru verb - special class">
<!ENTITY vn "irregular nu verb">
<!ENTITY vr "irregular ru verb, plain form ends with -ri">
<!ENTITY vs "noun or participle which takes the aux. verb suru">
<!ENTITY vs-c "su verb - precursor to the modern suru">
<!ENTITY vs-s "suru verb - special class">
<!ENTITY vs-i "suru verb - irregular">
<!ENTITY kyb "Kyoto-ben">
<!ENTITY osb "Osaka-ben">
<!ENTITY ksb "Kansai-ben">
<!ENTITY ktb "Kantou-ben">
<!ENTITY tsb "Tosa-ben">
<!ENTITY thb "Touhoku-ben">
<!ENTITY tsug "Tsugaru-ben">
<!ENTITY kyu "Kyuushuu-ben">
<!ENTITY rkb "Ryuukyuu-ben">
<!ENTITY nab "Nagano-ben">
<!ENTITY hob "Hokkaido-ben">
<!ENTITY vt "transitive verb">
<!ENTITY vulg "vulgar expression or word">
<!ENTITY adj-kari "`kari' adjective (archaic)">
<!ENTITY adj-ku "`ku' adjective (archaic)">
<!ENTITY adj-shiku "`shiku' adjective (archaic)">
<!ENTITY adj-nari "archaic/formal form of na-adjective">
<!ENTITY n-pr "proper noun">
<!ENTITY v-unspec "verb unspecified">
<!ENTITY v4k "Yodan verb with `ku' ending (archaic)">
<!ENTITY v4g "Yodan verb with `gu' ending (archaic)">
<!ENTITY v4s "Yodan verb with `su' ending (archaic)">
<!ENTITY v4t "Yodan verb with `tsu' ending (archaic)">
<!ENTITY v4n "Yodan verb with `nu' ending (archaic)">
<!ENTITY v4b "Yodan verb with `bu' ending (archaic)">
<!ENTITY v4m "Yodan verb with `mu' ending (archaic)">
<!ENTITY v2k-k "Nidan verb (upper class) with `ku' ending (archaic)">
<!ENTITY v2g-k "Nidan verb (upper class) with `gu' ending (archaic)">
<!ENTITY v2t-k "Nidan verb (upper class) with `tsu' ending (archaic)">
<!ENTITY v2d-k "Nidan verb (upper class) with `dzu' ending (archaic)">
<!ENTITY v2h-k "Nidan verb (upper class) with `hu/fu' ending (archaic)">
<!ENTITY v2b-k "Nidan verb (upper class) with `bu' ending (archaic)">
<!ENTITY v2m-k "Nidan verb (upper class) with `mu' ending (archaic)">
<!ENTITY v2y-k "Nidan verb (upper class) with `yu' ending (archaic)">
<!ENTITY v2r-k "Nidan verb (upper class) with `ru' ending (archaic)">
<!ENTITY v2k-s "Nidan verb (lower class) with `ku' ending (archaic)">
<!ENTITY v2g-s "Nidan verb (lower class) with `gu' ending (archaic)">
<!ENTITY v2s-s "Nidan verb (lower class) with `su' ending (archaic)">
<!ENTITY v2z-s "Nidan verb (lower class) with `zu' ending (archaic)">
<!ENTITY v2t-s "Nidan verb (lower class) with `tsu' ending (archaic)">
<!ENTITY v2d-s "Nidan verb (lower class) with `dzu' ending (archaic)">
<!ENTITY v2n-s "Nidan verb (lower class) with `nu' ending (archaic)">
<!ENTITY v2h-s "Nidan verb (lower class) with `hu/fu' ending (archaic)">
<!ENTITY v2b-s "Nidan verb (lower class) with `bu' ending (archaic)">
<!ENTITY v2m-s "Nidan verb (lower class) with `mu' ending (archaic)">
<!ENTITY v2y-s "Nidan verb (lower class) with `yu' ending (archaic)">
<!ENTITY v2r-s "Nidan verb (lower class) with `ru' ending (archaic)">
<!ENTITY v2w-s "Nidan verb (lower class) with `u' ending and `we' conjugation (archaic)">
<!ENTITY archit "architecture term">
<!ENTITY astron "astronomy, etc. term">
<!ENTITY baseb "baseball term">
<!ENTITY biol "biology term">
<!ENTITY bot "botany term">
<!ENTITY bus "business term">
<!ENTITY econ "economics term">
<!ENTITY engr "engineering term">
<!ENTITY finc "finance term">
<!ENTITY geol "geology, etc. term">
<!ENTITY law "law, etc. term">
<!ENTITY mahj "mahjong term">
<!ENTITY med "medicine, etc. term">
<!ENTITY music "music term">
<!ENTITY Shinto "Shinto term">
<!ENTITY shogi "shogi term">
<!ENTITY sports "sports term">
<!ENTITY sumo "sumo term">
<!ENTITY zool "zoology term">
<!ENTITY joc "jocular, humorous term">
<!ENTITY anat "anatomical term">"""
entities = entities.split('\n')
startentitytag, endentitytag = "<!ENTITY ", ">"
assert all(e.startswith(startentitytag) and e.endswith(endentitytag)
           for e in entities)
entities = [e[len(startentitytag):-len(endentitytag)] for e in entities]
entities = [(e[:i],e[i+1:]) for e, i in ((e, e.index(' ')) for e in entities)]
assert all(e[1].startswith('"') and e[1].endswith('"') for e in entities)
entities, revEntities = ({e[1][1:-1]:e[0] for e in entities},
                         {e[0]:e[1][1:-1] for e in entities})

def load():
    try:
        with open("questions/grammarPickle.pkl", 'rb') as f:
            dictionary = pickle.load(f)
    except FileNotFoundError:
        dictionary = {}
    return dictionary

def save():
    with open("questions/grammarPickle%s.pkl" %
              time.asctime().replace(' ', '_').replace(':','-'), 'wb') as f:
        pickle.dump(dictionary, f, -1)
    with open("questions/grammarPickle.pkl", 'wb') as f:
        pickle.dump(dictionary, f, -1)

dictionary = load()

vocab = voc.get_vocab()
inter = [q for q in vocab
         if (isinstance(q, voc.VocabKtoSQuestion) or
             isinstance(q, voc.VocabRtoSQuestion))]

revMap = defaultdict(lambda :defaultdict(set))
for q in inter:
    for entry in q.entries:
        for sense in q.entries[entry]:
            pos = frozenset(entities[pos] for pos in sense.poss)
            for gloss in sense.glosses:
                gloss = EnglishVerifier.normalize(gloss)
                revMap[gloss][pos].add(entry[0])
revMap.default_factory = None

def display_from_revMap(word):
    print("Word:", word)
    ents = []
    for pos in revMap[word]:
        for rep in revMap[word][pos]:
            print(rep, set(pos))

def display_from_dictionary(word):
    print("Word:", word)
    values, group = dictionary[word]
    print("Group:", set(group))
    print("Values:")
    for val in values:
        print(val)

def add(word):
    if word not in revMap:
        print(word, "not found")
        return
    display_from_revMap(word)
    if word in dictionary:
        print(word, "already added")
        display_from_dictionary(word)
        return
    dic_word = revMap[word]
    if len(dic_word) > 1:
        print("Multiple POS")
        pos = frozenset(input("Choose POS (ex: n.vs): ").split('.'))
    else:
        pos = frozenset(list(dic_word.keys())[0])
        print("POS:", set(pos))
    values = set()
    excluded = False
    for pos2 in dic_word:
        if pos.issubset(pos2):
            values.update(dic_word[pos2])
        else:
            excluded = True
    if len(values) == 0:
        print("No matches")
        return
    if excluded:
        word = word + "[" + '.'.join(pos) + "]"
        print("Some values excluded.")
        print("Word prompt:", word)
        print("New values:")
        for val in values:
            print(val)
    if len(values) == 1:
        print("Exactly one match, adding")
        dictionary[word] = (list(values), pos)
    else:
        print("Multiple matches")
        val = None
        while val not in values:
            val = input("Select primary: ")
        print("adding")
        dictionary[word] = (sorted(values, key=lambda v:0 if v == val else 1),
                            pos)
    display_from_dictionary(word)
