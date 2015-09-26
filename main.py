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

    save()

def setup():
    from questions.novel_frequency import get_questions
    from feed import CategoryFeed
    from scheduler import Jas1Scheduler
    from triage import CategoryReverseTriage
    from pack import CategoryPack
    from persist import Persist, replay
    questions = get_questions()
    qs = {question.q:question for question in questions}
    ordered = [(question.q, question.group) for question in questions]
    feed = CategoryFeed(ordered)
    pack = CategoryPack(feed, CategoryReverseTriage(),
                        Jas1Scheduler(), qs, Persist("records/records.txt"))
    replay("records/records.txt", pack, qs)
    with open(cacheFile, 'wb') as f:
        pickle.dump(pack, f, -1)
