def askQuestion(pack, context, time):
    q = pack.getQuestion(time)
    question = context[q]
    if q not in pack.feed.seen:
        print "New Question:"
        question.body()
    question.ask()
    ans = raw_input()
    correct = question.check(ans)
    if correct:
        print "Correct"
    else:
        print "Incorrect"
        print "Remember:"
        question.body()
    pack.record(q, correct, time)
    return correct
