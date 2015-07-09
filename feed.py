class Feed(object):
    def __init__(self, ordered):
        self.ordered = ordered
        self.orderedI = 0
        self.seen = set()

    def mark(self, q):
        self.seen.add(q)

    def getQuestion(self):
        while self.ordered[self.orderedI] in self.seen:
            self.orderedI += 1
        return self.ordered[self.orderedI]
