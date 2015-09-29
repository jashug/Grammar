from collections import namedtuple, defaultdict

class Jas1Scheduler(object):
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

class FullRecordScheduler(object):
    def __init__(self, sub):
        self.data = defaultdict(list)
        self.sub = sub

    def schedule(self, q, correct, time):
        self.data[q].append((time, correct))
        return self.sub.schedule(q, correct, time)

SM2Record = namedtuple('SM2Record', ('e_factor', 'interval', 'valid_after',))
class SM2Scheduler(object):
    def __init__(self, base_interval=60, starting_E_factor=2.5,
                 delta_E=(-0.1, 0), E_bound=(1.3, 2.5), post_factor=2):
        self.base_interval = base_interval
        self.starting_E_factor = starting_E_factor
        self.delta_E = delta_E
        self.E_bound = E_bound
        self.post_factor = post_factor
        self.data = {}

    def schedule(self, q, correct, time, commit=True):
        if q in self.data:
            rec = self.data[q]
            e_factor = rec.e_factor
        else:
            e_factor = self.starting_E_factor
        if correct and q in self.data:
            last_time = rec.valid_after - rec.interval
            actual_interval = time - last_time
            factor = 6 if rec.interval == self.base_interval else e_factor
            interval = max(min(factor * actual_interval,
                               self.post_factor * factor * rec.interval),
                           rec.interval)
        else:
            interval = self.base_interval
        if q in self.data:
            expected_failure = rec.valid_after + rec.interval * rec.e_factor
        if not (q in self.data and
                ((correct and time < rec.valid_after) or
                 (not correct and time > expected_failure))):
            e_factor += self.delta_E[correct]
        e_factor = max(min(e_factor, self.E_bound[1]), self.E_bound[0])
        if commit:
            self.data[q] = SM2Record(e_factor, interval, time + interval)
        return self.data[q].valid_after
