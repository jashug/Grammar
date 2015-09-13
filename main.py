import time
import pickle as pickle

from question_basics import recursive_children

cacheFile = "records/pack.pkl"

pack, context = None, None

def load():
    global pack, context
    if pack is None:
        with open(cacheFile, 'rb') as f:
            pack = pickle.load(f)

def save():
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)

def main():
    load()

    print("Welcome to the Quiz program (2.0)")
    pack.stats(time.time())
    input("Press enter to begin.")

    start = time.time()
    total, wrong = 0, 0

    with pack:
        try:
            while True:
                try:
                    current_time = time.time()
                    question = pack.get_question(current_time)
                    for child in recursive_children(question):
                        if child.q not in pack.feed.seen:
                            print("New Question:")
                            print(child.body)
                    print(question.prompt)
                    ans = input()
                    correct = question.check(ans)
                    if correct:
                        print("Correct!")
                    else:
                        print("Incorrect.")
                        if not pack.second_chance(question):
                            print("Remember:")
                            print(question.body)
                    pack.record(question, correct, current_time)
                except StopIteration as e:
                    print("Out of cards in:", e.value)
                    break

                if not correct: wrong += 1
                total += 1
        except KeyboardInterrupt:
            print("Finished.")

    end = time.time()
    dt = end - start

    pack.stats(time.time())
    print("You missed %d problems." % wrong)
    print("You answered %d problems in %d minutes %d seconds." %\
          (total, dt // 60, dt % 60))
    if total > 0:
        print("That is %.3f seconds per problem, or %.3f problems per minute"%\
              (dt / total, 60 * total / dt))
        print("Your accuracy was %d%%, or %s:1 right:wrong" %\
              (100*float(total-wrong)/total,
               ("%.1f"%(float(total-wrong)/wrong)) if wrong > 0 else "inf"))

    save()

def setup():
    from questions.grammarQuestions import addQuestions
    from feed import CategoryFeed
    from scheduler import Jas1Scheduler
    from triage import CategoryReverseTriage
    from pack import CategoryPack
    from persist import Persist, replay
    qs = {}
    ordered = addQuestions(qs, "questions/grammarPickle.pkl")
    feed = CategoryFeed(ordered)
    pack = CategoryPack(feed, CategoryReverseTriage(),
                        Jas1Scheduler(), qs, Persist("records/records.txt"))
    replay("records/records.txt", pack, qs)
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

setup()
main()
