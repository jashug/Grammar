# medley of <http://svn.python.org/projects/python/trunk/Lib/heapq.py>
# and <https://mail.python.org/pipermail/python-dev/attachments/20061105
#      /62f57d3a/attachment.obj>

class Heap(object):
    def __init__(self):
        self.heap = []
        self.map = {}

    def __contains__(self, x):
        return x in self.map

    def __len__(self):
        return len(self.heap)

    def put(self, x, p):
        if x in self.map:
            self._removeAt(self.map[x])
        self._add(x, p)

    def remove(self, x):
        self._removeAt(self.map[x])
        
    def pop(self):
        ret = self.heap[0]
        self._removeAt(0)
        return ret

    def peek(self):
        return self.heap[0]

    def _setheap(self, i, px):
        self.map[px[1]] = i
        self.heap[i] = px

    def _add(self, x, p):
        self.heap.append((p, x))
        self.map[x] = len(self.heap)-1
        self._siftdown(0, len(self.heap)-1)

    def _removeAt(self, posn):
        if posn < len(self.heap) - 1:
            del self.map[self.heap[posn][1]]
            self._setheap(posn, self.heap[-1])
            self.heap.pop()
            self._siftdown(0, posn)
            self._siftup(posn)
        else:
            del self.map[self.heap[posn][1]]
            self.heap.pop()

    def _siftdown(self, startpos, pos):
        newitem = self.heap[pos]
        # Follow the path to the root, moving parents down until finding a place
        # newitem fits.
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = self.heap[parentpos]
            if newitem < parent:
                self._setheap(pos, parent)
                pos = parentpos
                continue
            break
        self._setheap(pos, newitem)

    def _siftup(self, pos):
        endpos = len(self.heap)
        startpos = pos
        newitem = self.heap[pos]
        # Bubble up the smaller child until hitting a leaf.
        childpos = 2*pos + 1    # leftmost child position
        while childpos < endpos:
            # Set childpos to index of smaller child.
            rightpos = childpos + 1
            if rightpos < endpos:
                if not self.heap[childpos] < self.heap[rightpos]:
                    childpos = rightpos
            # Move the smaller child up.
            self._setheap(pos, self.heap[childpos])
            pos = childpos
            childpos = 2*pos + 1
        # The leaf at pos is empty now.  Put newitem there, and bubble it up
        # to its final resting place (by sifting its parents down).
        self._setheap(pos, newitem)
        self._siftdown(startpos, pos)

if __name__ == "__main__":
    print "Testing..."
    h = Heap()
    for i in range(10):
        h.put(chr(97+i), i)
    assert len(h) == 10
    h.put('b',5.5)
    h.put('f', 2.5)
    h.put('z',-1)
    h.remove('d')
    l = []
    while len(h) > 0:
        l.append(h.pop())
    assert l == [(-1, 'z'), (0, 'a'), (2, 'c'), (2.5, 'f'), (4, 'e'),
                 (5.5, 'b'), (6, 'g'), (7, 'h'), (8, 'i'), (9, 'j')]
    
    h = Heap()
    h.put('one', 96.2)
    h.put('person', 100.5)
    h.put('ten', 103.9)
    #print "After Puts:", h.heap, h.map
    assert h.pop()[1] == 'one'
    #print "After Pop:", h.heap, h.map
    h.put('one', 151.2)
    #print "After Put:", h.heap, h.map
    assert h.pop()[1] == 'person'
    print "Good!"
