from collections import defaultdict, deque

SOURCE, SINK = object(), object()

class FlowGraph(object):
    def __init__(self):
        self.graph = defaultdict(lambda: defaultdict(int))

    def copy(self):
        other = FlowGraph()
        for u in self.graph:
            for v in self.graph[u]:
                if self.graph[u][v] > 0:
                    other.add_edge(u, v, self.graph[u][v])
        return other

    def add_edge(self, u, v, capacity):
        assert capacity > 0
        self.graph[u][v] += capacity

    def find_path(self):
        prev, capacity = {}, {}
        queue = deque()
        queue.append(SOURCE)
        prev[SOURCE], capacity[SOURCE] = None, float('inf')
        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                if v in prev or self.graph[u][v] == 0:
                    continue
                assert self.graph[u][v] > 0
                prev[v], capacity[v] = u, min(capacity[u], self.graph[u][v])
                if v is SINK:
                    path = []
                    while u is not SOURCE:
                        path.append((u, v))
                        u, v = prev[u], u
                    path.append((u, v))
                    return path, capacity[SINK]
                queue.append(v)
        return None, 0

    def compute_max_flow(self):
        while True:
            path, flow = self.find_path()
            #print(path, flow)
            if flow == 0:
                break
            for u, v in path:
                assert self.graph[u][v] >= flow
                self.graph[u][v] -= flow
                self.graph[v][u] += flow
        sink_flow = sum(self.graph[SINK].values())
        source_flow = sum(self.graph[u][SOURCE] for u in self.graph)
        assert sink_flow == source_flow
        return sink_flow

if __name__ == '__main__':
    g = FlowGraph()
    g.add_edge(SOURCE,'o',3)
    g.add_edge(SOURCE,'p',3)
    g.add_edge('o','p',2)
    g.add_edge('o','q',3)
    g.add_edge('p','r',2)
    g.add_edge('r',SINK,3)
    g.add_edge('q','r',4)
    g.add_edge('q',SINK,2)
    flow = g.compute_max_flow()
    assert flow == 5
