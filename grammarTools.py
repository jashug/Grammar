# -*- coding: utf-8 -*-
import cPickle as pickle
import os
import time
from pprint import pprint
from collections import defaultdict
import itertools, functools

from questions.grammarQuestions import *
import questions.japQuestions as jap
import questions.vocabQuestions as voc

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
    with open("questions/grammarPickle.pkl", 'rb') as f:
        dictionary, oldCategories = pickle.load(f)
    return dictionary

dictionary = load()

def save():
    with open("questions/grammarPickle%s.pkl" %
              time.asctime().replace(' ', '_').replace(':','-'), 'wb') as f:
        pickle.dump((dictionary, categories), f, -1)
    with open("questions/grammarPickle.pkl", 'wb') as f:
        pickle.dump((dictionary, categories), f, -1)

qs = {}
order, kanjiOrder, vocabOrder, chunks = \
       jap.addJapaneseQuestions(qs, "questions/vocabPickle.pkl", False)
inter = [q for q in order if (q.startswith("vocabKS.") or
                              q.startswith("vocabRS"))]

def computePos(inter):
    poss = defaultdict(int)
    possets = defaultdict(int)
    for q in inter:
        for entry in qs[q].entries:
            for sense in entry[1]:
                partsofspeech = [entities[pos] for pos in sense[-1]]
                possets[tuple(sorted(set(partsofspeech)))] += 1
                for pos in partsofspeech:
                    poss[pos] += 1
    return poss, possets

poss, possets = computePos(inter)
rposs, rpossets = computePos(inter[:10000])

def posCategories(possets):
    categories = defaultdict(list)
    def name(pset):
        return 'C'+'.'.join(sorted(pset))
    def value(pset):
        return 'G'+'.'.join(sorted(pset))
    for pset in possets:
        for i in range(1, len(pset)+1):
            for subset in itertools.combinations(pset, i):
                categories[name(subset)].append(value(pset))
    return dict(categories)

categories = {
    'noun': ['Cn', 'Cn-adv', 'Cn-suf', 'Cn-pref', 'Cn-t'],
    'verb': ['Caux-v', 'Civ', 'Cv-unspec', 'Cv1', 'Cv1-s',
             'Cv2a-s', 'Cv2b-k', 'Cv2b-s', 'Cv2d-k', 'Cv2d-s',
             'Cv2g-k', 'Cv2g-s', 'Cv2h-k', 'Cv2h-s', 'Cv2k-k',
             'Cv2k-s', 'Cv2m-k', 'Cv2m-s', 'Cv2n-s', 'Cv2r-k',
             'Cv2r-s', 'Cv2s-s', 'Cv2t-k', 'Cv2t-s', 'Cv2w-s',
             'Cv2y-k', 'Cv2y-s', 'Cv2z-s', 'Cv4b', 'Cv4g', 'Cv4h', 'Cv4k',
             'Cv4m', 'Cv4n', 'Cv4r', 'Cv4s', 'Cv4t', 'Cv5aru', 'Cv5b',
             'Cv5g', 'Cv5k', 'Cv5k-s', 'Cv5m', 'Cv5n', 'Cv5r', 'Cv5r-i',
             'Cv5s', 'Cv5t', 'Cv5u', 'Cv5u-s', 'Cv5uru', 'Cvi', 'Cvk',
             'Cvn', 'Cvr', 'Cvs', 'Cvs-c', 'Cvs-i', 'Cvs-s', 'Cvt', 'Cvz'],
}
categories.update(posCategories(possets))

revMap = defaultdict(lambda :defaultdict(set))
for i in range(len(inter)):
    q = inter[i]
    for entry in qs[q].entries:
        for sense in entry[1]:
            pos = 'G'+'.'.join(sorted(entities[pos] for pos in sense[-1]))
            for gloss in sense[0]:
                gloss = voc.elimParens(gloss).lower().strip()
                revMap[gloss][pos].add((entry[0][0], i))
revMap.default_factory = None

def display_from_revMap(word):
    print "Word:", word
    ents = []
    for pos in revMap[word]:
        for rep, rank in revMap[word][pos]:
            ents.append((rep, rank, pos))
    ents.sort(key=lambda (rep, rank, pos):(rank, pos, rep))
    for rank, rep, pos in ents:
        print rank, rep, pos

def display_from_dictionary(word):
    print "Word:", word
    values, group, rank = dictionary[word]
    print "Group:", group
    print "Rank:", rank
    print "Values:"
    for val in values:
        print val

def add(word):
    if word not in revMap:
        print word, "not found"
        return
    display_from_revMap(word)
    if word in dictionary:
        print word, "already added"
        display_from_dictionary(word)
        return
    dic_word = revMap[word]
    if len(dic_word) > 1:
        print "Multiple POS"
        pos = 'G' + '.'.join(sorted(
            raw_input("Choose POS (ex: n.vs): ").split('.')))
    else:
        pos = dic_word.keys()[0]
        print "POS:", pos
    posset = set(pos[1:].split('.'))
    values = set()
    excluded = False
    for pos2 in dic_word:
        if posset.issubset(set(pos2[1:].split('.'))):
            values.update(dic_word[pos2])
        else:
            excluded = True
    if len(values) == 0:
        print "No matches"
        return
    if excluded:
        word = word + "[" + pos[1:] + "]"
        print "Some values excluded."
        print "Word prompt:", word
        print "New values:"
        for val, rank in sorted(values, key=lambda (val,rank):rank):
            print rank, val
    if len(values) == 1:
        print "Exactly one match, adding"
        val, rank = list(values)[0]
        dictionary[word] = ([val,], pos, rank)
        display_from_dictionary(word)
        return
    else:
        print "Multiple matches"
        values = dict(values)
        val = None
        while val not in values:
            val = raw_input("Select primary: ")
        print "adding"
        rank = values[val]
        dictionary[word] = (sorted(values.keys(),
                                   key=lambda v:-1 if v == val else values[v]),
                            pos, rank)
        display_from_dictionary(word)