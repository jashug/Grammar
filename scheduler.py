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

class AccuracyMeasurer(object):
    def __init__(self, sub, target_recall):
        self.sub = sub
        self.target_recall = target_recall
        self.data = {}
        self.var = 0
        self.correct = 0
        self.total_questions = 0

    def schedule(self, q, correct, time):
        if q in self.data:
            last_time, requested_time = self.data[q]
            r = self.target_recall ** ((time - last_time) /
                                       (requested_time - last_time))
            self.var += abs(int(correct) - r) ** 2
            self.correct += int(correct)
            self.total_questions += 1
        next_time = self.sub.schedule(q, correct, time)
        self.data[q] = (time, next_time)
        return next_time

### This is an extensively modified version of the SuperMemo 2 algorithm
### Algorithm SM-2, © Copyright SuperMemo World, 1991.  
### www.supermemo.com, www.supermemo.eu
### Neither this program nor this version of the algorithm
### are endorsed by SuperMemo World

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

### This is my interpertation of the SuperMemo 17 algorithm
### Algorithm SM-17 is currently under development,
### this work is based on http://www.supermemopedia.com/wiki/Algorithm_SM-17
### around October 2015
### www.supermemo.com, www.supermemo.eu
### Neither this program nor this version of the algorithm
### are endorsed by SuperMemo World

class SM17SIncRefiner(object):
    def __init__(self, sinc):
        self.sinc = sinc
        self.history = defaultdict(list)

    def schedule(self, q, correct, time, commit=True):
        if commit:
            self.history[q].append((time, correct))
        return None # this object is not a proper scheduler

    def refine_sinc(self):
        difficulty = {q:compute_difficulty(q) for q in self.history}
        # compute recall matrix
        recall = None
        for q in self.history:
            d = difficulty[q]
            lapsed, prelapse_r, lapse_num = True, None, 0
            for s, interval, correct in iterate_parameters(q):
                r = compute_r(s, interval)
                if lapsed:
                    pls[lapse_num, prelapse_r].record(interval, correct)
                else:
                    recall[d, s, r].record(correct)
                if correct:
                    lapsed = False
                else:
                    lapsed = True
                    lapse_num += 1
                    prelapse_r = r
        # compute updated sinc matrix
        new_sinc = None
        for q in self.history:
            d = difficulty[q]
            for s, interval, correct in iterate_parameters(q):
                if not correct:
                    continue
                r = compute_r(s, interval)
                s2_estimated = s * self.sinc[d, s, r].value
                s2_measured = recall[d, s2_estimated, r].s_value(interval)
                new_sinc[d, s, r].record(s2_measured / s)
        return new_sinc
