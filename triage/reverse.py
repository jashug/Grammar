from heap import Heap

class ReverseTriage(object):
    def __init__(self):
        self.queue = Heap()

    def schedule(self, q, time):
        self.queue.put(q, -time)

    def recommend(self, time):
        for t, q in self.queue:
            t = -t
            yield q

    def __contains__(self, q):
        return q in self.queue

    def remove(self, q):
        if q in self.queue:
            self.queue.remove(q)
