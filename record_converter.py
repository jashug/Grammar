from question_basics import uid, uidInv
from questions.kanjiQuestions import get_kanji

kanji = get_kanji()
kanji_heads = set(q.head for q in kanji)

old_record_copy = (r"C:\Users\Jasper Hugunin\Documents\JapTutor" +
                   r"\Quizzer\recordsCopyBeforeTransition.txt")
new_records = (r"C:\Users\Jasper Hugunin\Documents\JapTutor" +
               r"\Grammar\records\records.txt")
old, new = open(old_record_copy, 'r'), open(new_records, 'w')

def convert(in_file, out_file):
    complex_questions = 0
    pruned_questions = 0
    for line in in_file:
        assert line[-1] == '\n'
        line = line[:-1].split(' ')
        assert len(line) == 5
        if line[0].startswith("vocabKRS") or line[0].startswith("vocabKSR"):
            complex_questions += 1
            continue
        if (line[0].startswith("vocabKS.") and
            uidInv(line[0][8:]) in kanji_heads):
            pruned_questions += 1
            continue
        out_file.write("%s %s %s\n" % (uid(line[0]), line[1], line[3]))
    print("Complex:", complex_questions)
    print("Pruned:", pruned_questions)

convert(old, new)
