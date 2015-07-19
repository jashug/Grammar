from builder import CategoryQuestion, Literal, QuestionThunk

class SumQuestion(CategoryQuestion):
    q = 'Sum'
    body = "For '+', put the two sides together"
    def __init__(self, get):
        self.left = get('exp')
        self.right = get('leaf')
        self.prompt = '(%s + %s)' % (self.left.prompt, self.right.prompt)
        self.parts = [self.left, self.right]

class Leaf(CategoryQuestion):
    q = staticmethod(lambda c:'Leaf' + c)
    def __init__(self, get, c):
        self.body = "Either %s or %s" % (c, c.upper())
        self.prompt = c
        self.parts = [Literal([c, c.upper()], self)]
LeafQuestion = lambda c:QuestionThunk(Leaf, c)

def addQuestions(qs):
    ordered = []
    ordered.append((SumQuestion.q, 'sum'))
    qs[SumQuestion.q] = SumQuestion
    for c in "abcdefghij":
        question = LeafQuestion(c)
        ordered.append((question.q, 'leaf'))
        qs[question.q] = question
    return ordered, {'exp':['sum', 'leaf']}
