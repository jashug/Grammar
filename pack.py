from question_basics import stringify, recursive_children, ANY

class CategoryPack(object):
    def __init__(self, feed, triage, scheduler, context, persist):
        self.feed = feed
        self.triage = triage
        self.scheduler = scheduler
        self.context = context
        self.persist = persist
        self.stack = []

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
            self.stack.clear()
        second_chance = self.second_chance(question)
        if self.stack:
            self.stack.pop()
        if correct:
            for child in recursive_children(question):
                self.record_simple(child.q, True, time)
        else:
            if second_chance:
                self.stack.append((question, True))
                for child in reversed(question.children):
                    self.stack.append((child, False))
            else:
                self.record_simple(question.q, False, time)
                for child in recursive_children(question, False):
                    self.record_simple(child.q, True, time)
        if persist:
            self.persist.record(question, correct, time)
        return correct

    def record_simple(self, q, correct, time):
        group = self.feed.find(q)
        nextTime = self.scheduler.schedule(q, correct, time)
        self.triage.schedule(group, q, nextTime)

    def __enter__(self):
        return self.persist.__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.persist.__exit__(exc_type, exc_value, exc_tb)

    def stats(self, time):
        self.triage.stats(time)
        self.feed.stats()
