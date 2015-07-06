from heap import Heap

class ReverseTriage(object):
    def __init__(self):
        self.queue = Heap()

    def schedule(self, q, time):
        self.queue.put(q, -time)

    def recommend(self, time):
        if len(self.queue) > 0:
            t, q = self.queue.peek()
            return q
        return None
