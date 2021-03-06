import time
import pickle as pickle
import os.path

from question_basics import recursive_children
import stats

cacheFile = os.path.join(os.path.dirname(__file__), 'records', 'pack.pkl')
stats_path = os.path.join(os.path.dirname(__file__), 'records', 'stats.html')

pack = None

def load():
    global pack
    if pack is None:
        with open(cacheFile, 'rb') as f:
            pack = pickle.load(f)

def save(pack):
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)
    stats_html = stats.get_stats(pack)
    with open(stats_path, 'w') as f:
        f.write(stats_html)

def main():
    load()

    print("Welcome to the Quiz program (2.0)")
    print("Review Queue:", pack.triage.get_review_queue_size(time.time()))
    try:
        input("Press enter to begin.")
    except KeyboardInterrupt:
        print("Stopped.")
        return

    start = time.time()

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
                    ans = ""
                    while ans == "":
                        ans = input()
                    correct = question.check(ans)
                    if correct:
                        print("Correct!")
                    else:
                        print("### Incorrect ###")
                        if not pack.second_chance(question):
                            print("Remember:")
                            print(question.body)
                    pack.record(question, correct, current_time)
                except StopIteration as e:
                    print("Out of cards in:", e.value)
                    break
        except KeyboardInterrupt:
            print("Finished.")

    end = time.time()
    dt = end - start

    total, wrong, new = pack.stats()
    print("You learned %d new problems." % new)
    print("You missed %d problems." % wrong)
    print("You answered %d problems in %d minutes %d seconds." %\
          (total, dt // 60, dt % 60))
    if total > 0:
        print("That is %.3f seconds per problem, or %.3f problems per minute"%\
              (dt / total, 60 * total / dt))
        print("Your accuracy was %d%%, or %s:1 right:wrong" %\
              (100*float(total-wrong)/total,
               ("%.1f"%(float(total-wrong)/wrong)) if wrong > 0 else "inf"))

    save(pack)

def get_questions():
    from questions.novel_frequency import get_questions
    questions = get_questions()
    qs = {question.q:question for question in questions}
    ordered = [(question.q, question.group) for question in questions]
    return ordered, qs

def setup():
    from feed import CategoryFeed
    from scheduler import Jas1Scheduler, SM2Scheduler
    from triage import CategoryReverseTriage
    from pack import CategoryPack
    from persist import Persist, replay
    ordered, qs = get_questions()
    feed = CategoryFeed(ordered)
    pack = CategoryPack(feed, CategoryReverseTriage(),
                        SM2Scheduler(base_interval=60*5),
                        qs, Persist("records/records.txt"))
    replay("records/records.txt", pack, qs)
    save(pack)

import feed, scheduler, triage, pack as packs, persist

##def make_test_pack():
##    from questions.novel_frequency import get_questions
##    from feed import CategoryFeed
##    from scheduler import Jas1Scheduler, SM2Scheduler, FullRecordScheduler
##    from triage import CategoryReverseTriage
##    from pack import CategoryPack
##    from persist import DummyPersist, replay
##    questions = get_questions()
##    qs = {question.q:question for question in questions}
##    ordered = [(question.q, question.group) for question in questions]
##    feed = CategoryFeed(ordered)
##    pack = CategoryPack(feed, CategoryReverseTriage(),
##                        FullRecordScheduler(SM2Scheduler()),
##                        qs, DummyPersist())
##    replay("records/records.txt", pack, qs)
##    return pack
