import time
import cPickle as pickle

import builder

cacheFile = "records/pack.pkl"
contextFile = "records/context.pkl"

def main():
    global pack, context
    with open(cacheFile, 'rb') as f:
        pack = pickle.load(f)
    with open(contextFile, 'rb') as f:
        context = pickle.load(f)

    print "Welcome to the Quiz program (2.0)"
    pack.stats(time.time())
    sentry = raw_input("Press enter to begin (non-empty to stop): ")
    if sentry: return
    
    start = time.time()
    total, wrong = 0, 0

    with pack:
        while not sentry:
            try:
                correct = askQuestion(pack, context, time.time())
            except StopIteration as e:
                print "Out of cards in:", e.message
                break

            if not correct: wrong += 1
            total += 1
            sentry = raw_input("Continue? (non-empty to stop): ")

    end = time.time()
    dt = end - start

    pack.stats(time.time())
    print "You missed %d problems." % wrong
    print "You answered %d problems in %d minutes %d seconds." %\
          (total, dt // 60, dt % 60)
    if total > 0:
        print "That is %.3f seconds per problem, or %.3f problems per minute"%\
              (dt / total, 60 * total / dt)
        print "Your accuracy was %d%%, or %s:1 right:wrong" %\
              (100*float(total-wrong)/total,
               ("%.1f"%(float(total-wrong)/wrong)) if wrong > 0 else "inf")

    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

def packSimple():
    from questions.japQuestions import addJapaneseQuestions
    from feed import Feed
    from scheduler import Jas1Scheduler
    from triage import ReverseTriage
    from pack import Pack
    from persist import Persist, replay
    qs = {}
    ordered, kanji, vocab, chunks = \
             addJapaneseQuestions(qs, "questions/vocabPickle.pkl")
    print "Got questions"
    feed = Feed(ordered)
    pack = Pack(feed, ReverseTriage(),
                Jas1Scheduler(), Persist("records/records.txt"))
    replay("records/records.txt", pack)
    with open(contextFile, 'wb') as f:
        pickle.dump(qs, f, -1)
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

def packCategories():
    from questions.grammarQuestions import addQuestions
    from feed import CategoryFeed
    from scheduler import Jas1Scheduler
    from triage import CategoryReverseTriage
    from pack import CategoryPack
    from persist import Persist, replay
    qs = {}
    ordered, categories = addQuestions(qs, "questions/grammarPickle.pkl")
    feed = CategoryFeed(ordered, categories)
    pack = CategoryPack(feed, CategoryReverseTriage(),
                        Jas1Scheduler(), Persist("records/records.txt"))
    replay("records/records.txt", pack, qs)
    with open(contextFile, 'wb') as f:
        pickle.dump(qs, f, -1)
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

def packCategoriesTest():
    from questions.testCategoryQuestions import addQuestions
    from feed import CategoryFeed
    from scheduler import Jas1Scheduler
    from triage import CategoryReverseTriage
    from pack import CategoryPack
    from persist import Persist, replay
    qs = {}
    ordered, categories = addQuestions(qs)
    feed = CategoryFeed(ordered, categories)
    pack = CategoryPack(feed, CategoryReverseTriage(),
                        Jas1Scheduler(), Persist("records/records.txt"))
    replay("records/records.txt", pack, qs)
    with open(contextFile, 'wb') as f:
        pickle.dump(qs, f, -1)
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

setup = packCategories
askQuestion = builder.askQuestionCategories
