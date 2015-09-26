from question_basics import stringify, recursive_children, ANY

class Stats(object):
    def __init__(self, initial_questions):
        self.total = 0
        self.wrong = 0
        self.initial_questions = initial_questions

    def record(self, correct):
        self.total += 1
        if not correct:
            self.wrong += 1

class CategoryPack(object):
    def __init__(self, feed, triage, scheduler, context, persist):
        self.feed = feed
        self.triage = triage
        self.scheduler = scheduler
        self.context = context
        self.persist = persist
        self.stack = []
        self.stats_cache = None

    def get_simple_question(self, time):
        triage = self.triage.recommend(time)
        next(triage)
        feed = self.feed.getQuestion()
        next(feed)
        
        category, use_immature = yield
        while True:
            groups = self.feed.getGroups(category)
            out = triage.send((groups, use_immature))
            if out is StopIteration:
                try:
                    out = feed.send(groups)
                except StopIteration:
                    raise StopIteration(category)
            category, use_immature = yield out

    def get_new_question(self, time):
        simple_questions = self.get_simple_question(time)
        next(simple_questions)
        def get_full_question(category, data, use_immature=True):
            q = simple_questions.send((category, use_immature))
            question_factory = self.context[q]
            sub_categories = question_factory.child_categories(*data)
            children = [get_full_question(sub_category, sub_data)
                        for sub_category, sub_data in sub_categories]
            question = question_factory(*children)
            return question
        return get_full_question(ANY, (), False)

    def get_question(self, time):
        if self.stack:
            return self.stack[-1][0]
        else:
            return self.get_new_question(time)

    def stack_failure(self, question):
        return (self.stack and
                stringify(question) != stringify(self.stack[-1][0]))

    def second_chance(self, question):
        return not (self.stack and self.stack[-1][1])

    def record(self, question, correct, time, persist=True):
        for child in recursive_children(question):
            self.feed.mark(child.q)
        if self.stack_failure(question):
            while self.stack:
                stack_question, failed_before = self.stack.pop()
                if failed_before:
                    self.record_simple(stack_question.q, False, time)
                else:
                    for child in recursive_children(stack_question):
                        self.record_simple(child.q, False, time)
        would_get_second_chance = self.second_chance(question)
        if self.stack:
            self.stack.pop()
        if would_get_second_chance:
            if correct:
                for child in recursive_children(question):
                    self.record_simple(child.q, True, time)
            else:
                self.stack.append((question, True))
                for child in reversed(question.children):
                    self.stack.append((child, False))
        else:
            self.record_simple(question.q, correct, time)
        if persist:
            self.persist.record(question, correct, time)
        return correct

    def record_simple(self, q, correct, time):
        self.stats_cache.record(correct)
        group = self.feed.find(q)
        nextTime = self.scheduler.schedule(q, correct, time)
        self.triage.schedule(group, q, nextTime)

    def __enter__(self):
        self.stats_cache = Stats(len(self.feed.seen))
        return self.persist.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.persist.__exit__(exc_type, exc_value, exc_tb)

    def stats(self):
        return (self.stats_cache.total,
                self.stats_cache.wrong,
                len(self.feed.seen) - self.stats_cache.initial_questions,
                )
