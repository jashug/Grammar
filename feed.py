from collections import defaultdict

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
        print "You have learned %d/%d cards" % \
              (len(self.seen), len(self.ordered))

class CategoryFeed(object):
    def __init__(self, ordered, categories):
        self.ordered = []
        self.mapping = {}
        self.indexes = defaultdict(list)
        for i in range(len(ordered)):
            q, group = ordered[i]
            self.ordered.append(q)
            self.mapping[q] = group
            self.indexes[group].append(i)
        for group in self.indexes:
            self.indexes[group].append(len(self.ordered))
        self.ordered.append(None)
        self.iters = {}
        self.categories = categories
        assert '*' not in self.categories
        self.categories['*'] = []
        for group in self.indexes:
            self.iters[group] = 0
            assert group not in self.categories
            self.categories[group] = [group,]
            self.categories['*'].append(group)
        self.seen = set()

    def update(self, iters, group):
        index = self.indexes[group]
        while self.ordered[index[iters[group]]] in self.seen:
            iters[group] += 1

    def mark(self, q):
        self.seen.add(q)
        self.update(self.iters, self.mapping[q])

    def getQuestion(self):
        iters = self.iters.copy()
        groups = yield
        while True:
            q = self.ordered[min(self.indexes[group][iters[group]]
                                 for group in groups)]
            if q is None:
                raise StopIteration(groups)
            iters[self.mapping[q]] += 1
            self.update(iters, self.mapping[q])
            groups = yield q

    def getGroups(self, category):
        return self.categories[category]

    def find(self, q):
        return self.mapping[q]

    def stats(self):
        pass
