class Pack(object):
    def __init__(self, feed, triage, scheduler, context, persist):
        self.feed = feed
        self.triage = triage
        self.scheduler = scheduler
        self.context = context
        self.persist = persist

    def getQuestion(self, time, use_immature=False):
        try:
            q, immature = self.triage.recommend(time).next()[1]
            if immature and not use_immature:
                raise StopIteration()
            return q
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
        next(triage)
        feed = self.feed.getQuestion()
        next(feed)
        
        category, use_immature = yield
        while True:
            groups = self.feed.getGroups(category)
            try:
                out, immature = triage.send(groups)
                if immature and not use_immature:
                    raise StopIteration()
            except StopIteration:
                try:
                    out = feed.send(groups)
                except StopIteration:
                    raise StopIteration(category)
            category, use_immature = yield out

    def record(self, q, correct, time, persist=True):
        self.feed.mark(q)
        group = self.feed.find(q)
        nextTime = self.scheduler.schedule(q, correct, time)
        self.triage.schedule(group, q, nextTime)
        if persist:
            self.persist.record(q, correct, time)
