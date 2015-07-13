from collections import defaultdict
from heap import Heap

class Expire(object):
    def __init__(self, triage):
        self.triage = triage
        self.queue = Heap()

    def schedule(self, q, time):
        self.triage.remove(q)
        self.queue.put(q, time)

    def shift(self, time):
        while len(self.queue) > 0 and self.queue.peek()[0] <= time:
            t, q = self.queue.pop()
            self.triage.schedule(q, t)

    def recommend(self, time):
        self.shift(time)
        return self.triage.recommend(time)

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)
        self.triage.remove(q)

    def stats(self, time):
        self.shift(time)
        self.triage.stats(time)

class Reverse(object):
    def __init__(self):
        self.queue = Heap()

    def schedule(self, q, time):
        self.queue.put(q, -time)

    def recommend(self, time):
        for t, q in self.queue:
            yield t, q

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)

    def stats(self, time):
        print "Review queue: %d" % len(self.queue)

def ReverseTriage():
    return Expire(Reverse())

class Category(object):
    def __init__(self, triageClass):
        self.groups = defaultdict(triageClass)

    def schedule(self, group, q, time):
        self.groups[group].schedule(q, time)

    def recommend(self, time):
        def attempt(it):
            try:
                return it.next()
            except:
                return float('inf'), None
        iters, saved = {}, {}
        for group in self.groups:
            iters[group] = self.groups[group].recommend(time)
            saved[group] = attempt(iters[group])
        groups = yield
        while True:
            (t, q), group = min((saved[group], group) for group in groups)
            if t == float('inf'):
                raise StopIteration()
            saved[group] = attempt(iters[group])
            groups = yield q

    def stats(self, time):
        pass

def CategoryReverseTriage():
    return Category(ReverseTriage)
