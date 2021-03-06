from collections import defaultdict
from itertools import chain
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
        out = self.triage.recommend(time)
        return chain(self.triage.recommend(time),
                     ((t, (q, True)) for t, q in self.queue))

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)
        self.triage.remove(q)

    def stats(self, time):
        self.shift(time)
        self.triage.stats(time)

    def get_review_queue_size(self, time):
        self.shift(time)
        return self.triage.get_review_queue_size(time)

class Reverse(object):
    def __init__(self):
        self.queue = Heap()

    def schedule(self, q, time):
        self.queue.put(q, -time)

    def recommend(self, time):
        for t, q in self.queue:
            yield t, (q, False)

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)

    def stats(self, time):
        print("Review queue: %d" % len(self.queue))

    def get_review_queue_size(self, time):
        return len(self.queue)

def ReverseTriage():
    return Expire(Reverse())

class Category(object):
    def __init__(self, triageClass):
        self.groups = defaultdict(triageClass)

    def schedule(self, group, q, time):
        self.groups[group].schedule(q, time)

    def recommend(self, time):
        inf = (float('inf'), (None, True))
        def attempt(it):
            try:
                return next(it)
            except StopIteration:
                return inf
        iters, saved = {}, defaultdict(lambda :inf)
        for group in self.groups:
            iters[group] = self.groups[group].recommend(time)
            saved[group] = attempt(iters[group])
        groups, use_immature = yield
        while True:
            group = min(groups, key=lambda group:saved[group])
            t, (q, immature) = saved[group]
            if t == float('inf') or immature and not use_immature:
                q = StopIteration
            else:
                saved[group] = attempt(iters[group])
            groups, use_immature = yield q

    def stats(self, time):
        pass

    def get_review_queue_size(self, time):
        return sum(self.groups[group].get_review_queue_size(time)
                   for group in self.groups)

def CategoryReverseTriage():
    return Category(ReverseTriage)
