class Vertex:
    def __init__(self, id):
        self.id = id
        self.adjacent = {}
        self.visitor = []

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent

    def get_connections_keys(self):
        return self.adjacent.keys()

    def get_connections_vals(self):
        return self.adjacent.values()

    def get_next_stop(self):
        return self.adjacent.values()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return int(self.adjacent[neighbor.get_id()])

    def get_weight_fromID(self, neighborID):
        return int(self.adjacent[neighborID])

    def add_visitor(self, boat):
        self.visitor.append(boat)

    def remove_visitor(self, boat):
        self.visitor.remove(boat)

    def get_visitors(self):
        return self.visitor

    def __str__(self):
        return 'Station' + str(self.id) + ' has route to: ' \
               + str([x.id for x in self.adjacent]) + ' with distance ' \
               + str([self.get_weight(x) for x in self.adjacent])

    # def __repr__(self):
    #     return str("This is Station %d" %(self.id))


class Graph:
    def __init__(self):
        self.stop_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.stop_dict.values())

    def createBasic3(self):
        self.add_stop(1)
        self.add_stop(2)
        self.add_stop(3)

        self.add_edge(1, 2, 10)
        self.add_edge(2, 3, 20)
        self.add_edge(3, 1, 50)

        return self

    def createBasic3Split(self):
        self.add_stop(1)
        self.add_stop(2)
        self.add_stop(3)
        self.add_stop(4)

        self.add_edge(1, 2, 10)
        self.add_edge(1, 4, 5)
        self.add_edge(4, 2, 10)
        self.add_edge(2, 3, 20)
        self.add_edge(3, 1, 50)

        return self

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.stop_dict:
            self.add_stop(frm)
        if to not in self.stop_dict:
            self.add_stop(to)

        self.stop_dict[frm].add_neighbor(to, cost)
        #self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def add_stop(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.stop_dict[node] = new_vertex
        return new_vertex

    def get_if_stop(self, n):
        if n in self.stop_dict:
            return self.stop_dict[n]
        else:
            return None

    def get_stop_dict(self):
        return self.stop_dict

    def get_stop_object(self):
        return self.stop_dict.values()

    def get_mat(self):
        mat = []
        for x in self.stop_dict.values():
            mat.append(x.get_visitors())
        return mat

    def print_mat(self):
        mat = []
        for x in self.stop_dict.values():
            mat.append(x.get_visitors())
        print(mat)



    def getNetwork(self):
        print("\t...Printing Network")
        for v in self.get_stop_object():
            for w in v.get_connections():
                vid = v.get_id()
                wid = w
                #vid = v.get_id()
                #wid = w.get_id()
                print('\t\t%s,%s,%3d' % (vid, wid, v.get_weight_fromID(w)))
        # for v in g:
        #     v.printNeighbors()
        #

class Controller_Map:
    def __init__(self):
        print("STARTING MAP CONTROLLER")
        self.map = Graph()
        self.basic_map()

    def basic_map(self):
        self.map.createBasic3Split()
        self.map.getNetwork()

    def getMap(self):
        return self.map
