class Pack(object):
    def __init__(self, feed, triage, scheduler, persist):
        self.feed = feed
        self.triage = triage
        self.scheduler = scheduler
        self.persist = persist

    def getQuestion(self, time):
        try:
            return self.triage.recommend(time).next()[1]
        except StopIteration:
            return self.feed.getQuestion()

    def record(self, q, correct, time, persist=True):
        self.feed.mark(q)
        nextTime = self.scheduler.schedule(q, correct, time)
        self.triage.schedule(q, nextTime)
        if persist:
            self.persist.record(q, correct, time)

    def __enter__(self):
        return self.persist.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.persist.__exit__(exc_type, exc_value, exc_tb)

    def stats(self, time):
        self.triage.stats(time)
        self.feed.stats()

class CategoryPack(Pack):
    def getQuestion(self, time):
        triage = self.triage.recommend(time)
        triage.next()
        feed = self.feed.getQuestion()
        feed.next()
        
        category = yield
        while True:
            groups = self.feed.getGroups(category)
            try:
                category = yield triage.send(groups)
            except StopIteration:
                try:
                    category = yield feed.send(groups)
                except StopIteration:
                    raise StopIteration(category)

    def record(self, q, correct, time, persist=True):
        self.feed.mark(q)
        group = self.feed.find(q)
        nextTime = self.scheduler.schedule(q, correct, time)
        self.triage.schedule(group, q, nextTime)
        if persist:
            self.persist.record(q, correct, time)
