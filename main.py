import time
import cPickle as pickle

from builder.simple import askQuestion

cacheFile = "records/pack.pkl"
contextFile = "records/context.pkl"

def main():
    global pack, context
    with open(cacheFile, 'rb') as f:
        pack = pickle.load(f)
    with open(contextFile, 'rb') as f:
        context = pickle.load(f)

    print "Welcome to the Quiz program (2.0)"
    sentry = raw_input("Press enter to begin (non-empty to stop): ")
    if sentry: return
    
    start = time.time()
    total, wrong = 0, 0

    with pack:
        while not sentry:
            correct = askQuestion(pack, context, time.time())

            if not correct: wrong += 1
            total += 1
            sentry = raw_input("Continue? (non-empty to stop): ")

    end = time.time()
    dt = end - start

    print "You missed %d problems." % wrong
    print "You answered %d problems in %d minutes %d seconds." %\
          (total, dt // 60, dt % 60)
    print "That is %.3f seconds per problem, or %.3f problems per minute" %\
          (dt / total, 60 * total / dt)
    print "Your accuracy was %d%%, or %s:1 right:wrong" %\
          (100*float(total-wrong)/total,
           ("%.1f"%(float(total-wrong)/wrong)) if wrong > 0 else "inf")

    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

def pack():
    from questions.japQuestions import addJapaneseQuestions
    from feed import Feed
    from schedule.jas1 import Jas1Scheduler
    from triage.expire import Expire
    from triage.reverse import ReverseTriage
    from pack.simple import Pack
    from persist import Persist, replay
    qs = {}
    ordered, kanji, vocab, chunks = \
             addJapaneseQuestions(qs, "questions/vocabPickle.pkl")
    print "Got questions"
    feed = Feed(ordered)
    pack = Pack(feed, Expire(ReverseTriage()),
                Jas1Scheduler(), Persist("records/records.txt"))
    #replay("records/records.txt", pack)
    with open(contextFile, 'wb') as f:
        pickle.dump(qs, f, -1)
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)
