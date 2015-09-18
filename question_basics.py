import base64

def recursive_children(question, include_root=True):
    out = []
    if include_root:
        out.append(question)
    for child in question.children:
        out += recursive_children(child)
    return out

def surrogateescape(s):
    """Transform a string suitable for printing in IDLE.

    Astral plane characters are transformed into surrogate escape sequences.
    """
    l = []
    for c in s:
        o = ord(c)
        if o < 0:
            raise UnicodeError("Negative codepoint", o)
        elif o <= 0xffff:
            # Basic multilingual plane
            l.append(c)
        elif o <= 0x10ffff:
            # Astral plane -> surrogate pair
            o2 = o - 0x10000
            l.append(chr(0xd800 + ((o2 & 0xffc00) >> 10)) +
                     chr(0xdc00 + (o2 & 0x3ff)))
        else:
            raise UnicodeError("Non unicode code point encountered", o)
    return ''.join(l)

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

def regSpace(s):
    out = [[]]
    for c in s:
        if c == ' ': out.append([])
        else: out[-1].append(c)
    return ' '.join(''.join(word) for word in out if word)

def elimParens(s):
    """Remove parenthesized portions of s."""
    out = []
    i = 0
    for c in s:
        if c == '(': i += 1
        elif c == ')': i -= 1
        elif i == 0: out.append(c)
        if i < 0: raise Exception("Unbalenced parens: %s"%s)
    if i != 0: raise Exception("Unbalenced parens: %s"%s)
    return regSpace(''.join(out))

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

class SimpleLeafQuestion(CategoryQuestion):
    group = "SimpleLeafQuestion"

    @property
    def parts(self):
        return [self.verifier,]

    def child_categories(self):
        return ()

    def __call__(self):
        return self

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

class UnsatisfiableError(ValueError):
    pass

class SimpleVerifier(object):
    @staticmethod
    def normalize(ans):
        return ans

    def __init__(self, values):
        self.values = [self.normalize(value) for value in values]
        self.values = [value for value in self.values if value]
        if not self.values:
            raise UnsatisfiableError("No valid values", values, type(self))

    def attempt(self, ans, loc):
        assert loc == {0}
        if self.normalize(ans) in self.values:
            return {len(ans)}
        return set()

class EnglishVerifier(SimpleVerifier):
    class Whitelist(object):
        def __init__(self, whitelist):
            self.whitelist = set(ord(c) for c in whitelist)

        def __getitem__(self, i):
            if i in self.whitelist:
                raise LookupError()

    translation_table = Whitelist('0123456789abcdefghijklmnopqrstuvwxyz ')

    @classmethod
    def normalize(cls, ans):
        ans = elimParens(ans)
        ans = ans.lower().translate(cls.translation_table)
        ans = regSpace(ans)
        return ans
