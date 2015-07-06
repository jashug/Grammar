from schedule.jas1 import Jas1Scheduler as Scheduler
from triage.expire import Expire
from triage.reverse import ReverseTriage as NaiveReverseTriage
ReverseTriage = lambda: Expire(NaiveReverseTriage())
