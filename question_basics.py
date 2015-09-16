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

class AnyCategory(object):
    def __str__(self):
        return "ANY"

    def __call__(self, group):
        return True
ANY = AnyCategory()

class Category(object):
    def __init__(self, groups):
        self.groups = set(groups)

    def __repr__(self):
        return "Category(%r)" % self.groups

    def __str__(self):
        return str(self.groups)

    def __call__(self, group):
        return group in self.groups

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
