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

def askQuestionCategories(pack, context, time):
    gen = pack.getQuestion(time)
    gen.next()
    def get(category, use_immature=True):
        q = gen.send((category, use_immature))
        question = context[q](get)
        if q not in pack.feed.seen:
            print "New Question:"
            print question.body
        return question
    def put(q, correct):
        pack.record(q, correct, time)
    question = get('*', False)
    print question.prompt
    ans = raw_input()
    correct, blame = question.check(put, ans)
    if correct:
        print "Correct!"
    else:
        print "Incorrect."
        print "Remember:"
        print blame.body
    return correct

class QuestionThunk(object):
    def __init__(self, Q, *args, **kwargs):
        self.q = Q.q(*args, **kwargs)
        self.Q = Q
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self, get):
        out = self.Q(get, *self.args, **self.kwargs)
        out.q = self.q
        return out

class CategoryQuestion(object):
    def check(self, put, ans):
        loc = set([0])
        for part in self.parts:
            loc, blame = part.attempt(put, ans, loc)
            if len(loc) == 0:
                return False, blame
        if len(ans) in loc:
            put(self.q, True)
            return True, None
        else:
            put(self.q, False)
            return False, self

    def attempt(self, put, ans, loc=set([0])):
        for part in self.parts:
            loc, blame = part.attempt(put, ans, loc)
            if len(loc) == 0:
                return loc, blame
        put(self.q, True)
        return loc, None

class Literal(object):
    def __init__(self, values, blame):
        self.values = values
        self.blame = blame
        
    def attempt(self, put, ans, loc):
        out = set()
        for i in loc:
            for v in self.values:
                if ans.startswith(v, i):
                    out.add(i + len(v))
        if len(out) == 0:
            put(self.blame.q, False)
            return out, self.blame
        else:
            return out, None
