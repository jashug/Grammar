from collections import defaultdict
from question_basics import ALL

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

    def stats(self):
        print("You have learned %d/%d cards" % \
              (len(self.seen), len(self.ordered)))

class CategoryFeed(object):
    def __init__(self, ordered):
        assert ordered
        self.categories = defaultdict(set)
        self.ordered = []
        self.mapping = {}
        self.indexes = defaultdict(list)
        self.iters = {}
        for i in range(len(ordered)):
            q, group = ordered[i]
            self.ordered.append(q)
            self.mapping[q] = group
            self.indexes[group].append(i)
            for category in group:
                self.categories[category].add(group)
            self.categories[ALL].add(group)
        for group in self.indexes:
            self.indexes[group].append(len(self.ordered))
            self.iters[group] = 0
        self.ordered.append(None)
        self.seen = set()

    def update(self, iters, group):
        index = self.indexes[group]
        while self.ordered[index[iters[group]]] in self.seen:
            iters[group] += 1

    def mark(self, q):
        self.seen.add(q)
        self.update(self.iters, self.mapping[q])

    def getIndex(self, iters, group):
        if group not in iters or group not in self.indexes:
            return len(self.ordered) - 1
        if iters[group] >= len(self.indexes[group]):
            return len(self.ordered) - 1
        return self.indexes[group][iters[group]]

    def getQuestion(self):
        iters = self.iters.copy()
        groups = yield
        while True:
            q = self.ordered[min(self.getIndex(iters, group)
                                 for group in groups)]
            if q is None:
                raise StopIteration(groups)
            iters[self.mapping[q]] += 1
            self.update(iters, self.mapping[q])
            groups = yield q

    def getGroups(self, category):
        if category == ALL:
            return self.indexes.keys()
        else:
            out = [group for group in self.indexes if category in group]
            if not out:
                raise Exception("No groups match category.", category)
            return out

    def find(self, q):
        return self.mapping[q]

    def stats(self):
        pass
