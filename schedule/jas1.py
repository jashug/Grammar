def Jas1Scheduler(object):
    def __init__(self, ratio=2, limit=4, baseInterval=10):
        self.lastTimes = {}
        self.ratio = ratio
        self.limit = limit
        self.baseInterval = baseInterval

    def schedule(self, q, correct, time, commit=True):
        if correct and q in self.lastTimes:
            lastTime, lastInterval = self.lastTimes[q]
            interval = min(self.ratio * (time - lastTime),
                           self.limit * lastInterval)
            if interval < lastInterval: interval = lastInterval
        else:
            interval = self.baseInterval
        if commit:
            self.lastTimes[q] = time, interval
        return time + interval
