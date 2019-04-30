class Strategies:

    def __init__(self, map):
        self.map = map

    @staticmethod
    def closest_neighbor(map, boat):
        options = boat.get_location().get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = map.get_station_object(closest_tuple[0][0])
        return closest_stop

class Dijkstra:
    # ---------USE LIKE THIS:---------
    # dijk = Strategies.Dijkstra(map)
    # path = dijk.run(1, 7)
    # print("Path: %s" % path)
    def __init__(self, map):
        self.map = map
        self.openList = []
        self.closedList = []
        self.debug = False


    def run(self, frm, to):
        self.fromto = [frm, to]
        # Starting with departure Vertex
        self.openList.append(DijkHeap(self.fromto[0], 0))
        self.expand(self.openList[0])
        # Loop (while not found, determine the next chosen one)
        dist = False
        while not dist:
            dist = self.expand(self.choose_cheapest_from_openlist())
        return dist

    def expand(self, element):
        self.openList.remove(element)
        self.closedList.append(element)
        # IF found destination, trace back the path
        if element.getID() == self.fromto[1]:
            if self.debug: print("FOUND DESTINATION! From %d to %d, distance = %d"%(self.fromto[0], self.fromto[1], element.getDist()))
            path = []
            current = element
            while current is not None:
                path.append(current.getID())
                current = current.parent
            path.append([element.getDist()])
            return path[::-1]  # Return reversed path
        # creating list of neighbors to expand
        nextPushesList = list(self.map.get_station_object(element.getID()).get_connections().items())
        if self.debug: print("Next to expand: %s, its Neighbors: %s" % (element, nextPushesList))

        for new in nextPushesList:
            new_in_closed = True
            new_in_open = True
            existing_in_open = None
            for closed in self.closedList:
                if new[0] == closed.getID():
                    new_in_closed = False
            for open in self.openList:
                if new[0] == open.getID():
                    new_in_open = False
                    existing_in_open = open
            if not new_in_closed: pass #ignore
            elif new_in_open:
                #add it to open
                self.openList.append(DijkHeap(new[0], (new[1] + element.getDist()), element))
            elif not new_in_open:
                #check if this is better option
                if new[1] + element.getDist() < existing_in_open.getDist():
                    self.openList.append(DijkHeap(new[0], (new[1] + element.getDist()), element))

        if self.debug: print("All open elements: %s" % self.openList)
        if self.debug: print("All closed elements: %s" % self.closedList)
        if self.debug: print()

    def choose_cheapest_from_openlist(self):
        if len(self.openList)>0:
            # Getting first unexpanded
            tmp = self.openList[0]
            # Getting better option
            for element in self.openList:
                if (element.getDist() < tmp.getDist()):
                    tmp = element
        else:
            print("ERROR: Open List is empty")
            return False
        return tmp

class DijkHeap:
    def __init__(self, vertex, distance, parent=None):
        self.vert = vertex
        self.dist = distance
        self.expanded = False
        self.parent = parent

    def getID(self):
        return self.vert

    def getDist(self):
        return self.dist

    def expanded(self):
        return self.expanded

    def __str__(self):
        return ("V%d:%i" %(self.vert, self.dist))

    def __repr__(self):
        return ("V%d:%i:%s" % (self.vert, self.dist, self.expanded))