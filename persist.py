class Persist(object):
    def __init__(self, backingFileName):
        self.path = backingFileName
        self.outFile = None

    def __enter__(self):
        self.outFile = open(self.path, 'a')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.outFile.close()
        self.outFile = None

    def record(self, q, correct, time):
        self.outFile.write("%(tag)s %(time).3f %(grade)s\n" % {
            'tag': q, 'time':time, 'grade':'1' if correct else '0'})

def replay(backingFile, pack, qs):
    with open(backingFile, 'r') as f:
        for line in f:
            assert line[-1] == '\n'
            q, time, correct = line[:-1].split()
            q, time, correct = q, float(time), correct == '1'
            if q in qs:
                pack.record(q, correct, time, False)
    return pack
