import base64

def recursive_children(question, include_root=True):
    out = []
    if include_root:
        out.append(question)
    for child in question.children:
        out += recursive_children(child)
    return out

def uid(s):
    """Generate a unique ASCII string for a unicode string."""
    return base64.urlsafe_b64encode(s.encode("UTF-8")).decode('ascii')

def uidInv(s):
    """uidInv(uid(s)) == s"""
    try:
        return base64.urlsafe_b64decode(s.encode('ascii')).decode('utf-8')
    except:
        print(repr(s))
        raise

def stringify(question):
    tail = ''
    if question.children:
        children = (stringify(child) for child in question.children)
        return uid(question.q + ' ' + ' '.join(children))
    else:
        return uid(question.q)

def destringify(q, context):
    def parse(q):
        tokens = uidInv(q).split(' ')
        question_factory = context[tokens[0]]
        children = [parse(child_q) for child_q in tokens[1:]]
        question = question_factory(*children)
        return question
    question = parse(q)
    return question

class Filter(object):
    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)

    def __invert__(self):
        return NotFilter(self)

    def without(self, tag):
        return WithoutFilter(self, tag)

class AnyFilter(Filter):
    def __call__(self, group):
        return True

    def __str__(self):
        return 'ANY'

class NoneFilter(Filter):
    def __call__(self, group):
        return False

    def __str__(self):
        return 'NONE'

class AndFilter(Filter):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, group):
        return self.left(group) and self.right(group)

    def __str__(self):
        return '(%s & %s)' % (self.left, self.right)

class OrFilter(Filter):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, group):
        return self.left(group) or self.right(group)

    def __str__(self):
        return '(%s | %s)' % (self.left, self.right)

class NotFilter(Filter):
    def __init__(self, child):
        self.child = child

    def __call__(self, group):
        return not self.child(group)

    def __str__(self):
        return '(~%s)' % self.child

class WithoutFilter(Filter):
    def __init__(self, child, tag):
        self.child = child
        self.tag = tag

    def __call__(self, group):
        return (self.tag not in group and
                self.child(frozenset(list(group) + [self.tag,])))

    def __str__(self):
        return "(%s.without('%s'))" % (self.child, self.tag)

class Tag(Filter):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, group):
        return self.tag in group

    def __str__(self):
        return "Tag('%s')" % self.tag

ANY = AnyFilter()
NONE = NoneFilter()

class CategoryQuestion(object):
    def __init__(self, *children):
        self.children = children

    def check(self, ans):
        loc = set([0])
        for part in self.parts:
            loc = part.attempt(ans, loc)
        return len(ans) in loc

    def attempt(self, ans, loc):
        for part in self.parts:
            loc = part.attempt(ans, loc)
        return loc

class Literal(object):
    def __init__(self, values):
        self.values = values
        
    def attempt(self, ans, loc):
        out = set()
        for i in loc:
            for v in self.values:
                if ans.startswith(v, i):
                    out.add(i + len(v))
        return out
