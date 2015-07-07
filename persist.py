def Persist(object):
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
