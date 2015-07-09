from heap import Heap

class Expire(object):
    def __init__(self, triage):
        self.triage = triage
        self.queue = Heap()

    def schedule(self, q, time):
        self.triage.remove(q)
        self.queue.put(q, time)

    def recommend(self, time):
        while len(self.queue) > 0 and self.queue.peek()[0] <= time:
            t, q = self.queue.pop()
            self.triage.schedule(q, t)
        return self.triage.recommend(time)

    def __contains__(self, q):
        return q in self.queue or q in self.triage

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)
        if q in self.triage:
            self.triage.remove(q)
