class Dijk():
    # ---------USE LIKE THIS:---------
    # dijk = Strategies.Dijkstra(map)
    # path = dijk.run(1, 7)
    # print("Path: %s" % path)
    def __init__(self, map):
        #Strategies.__init__(self, map)
        self.map = map

    def run(self, frm, to):
        if frm == to:
            return[[0],frm]

        self.debug = False
        #if frm==to: return [[0]]
        ol = []
        cl = []
        self.fromto = [frm, to]
        # Starting with departure Vertex
        ol.append(DijkHeap(self.fromto[0], 0))
        dist = self.expand(ol[0], ol, cl)
        # Loop (while not found, determine the next chosen one)
        return dist


    def expand(self, element, ol, cl):
        #Todo heres the bug
        ol.remove(element)
        cl.append(element)
        # IF found destination, trace back the path
        if (element.getID() == self.fromto[1] and len(cl)!=1) or (element.getID() == self.fromto[0] and len(cl)>1):
            if self.debug: print("FOUND DESTINATION! From %d to %d, distance = %d"%(self.fromto[0], self.fromto[1], element.getDist()))
            path = []
            current = element
            tot_dist = 0
            while current is not None:
                path.append(current.getID())
                current = current.parent
            path.append([element.dist])
            return path[::-1] # Return reversed path
        # creating list of neighbors to expand
        #nextPushesList = list(self.map.get_station(element.getID()).get_connections().items())
        nextPushesList = sorted(list(self.map.get_station(element.getID()).get_connections().items()), key=lambda x: x[1])
        if self.debug: print("Next to expand: %s, its Neighbors: %s" % (element, nextPushesList))
        for new in nextPushesList:
            loop_found = False
            new_element_already_in_closed = False
            new_element_already_in_open = False
            existing_in_open = None
            for closed in cl:
                if new[0] == closed.getID():
                    new_element_already_in_closed = True
            if new_element_already_in_closed: continue
            if new[0] == self.fromto[0]:
                loop_found = True
                pass
            for open in ol:
                if new[0] == open.getID():
                    new_element_already_in_open = True
                    existing_in_open = open
            if not new_element_already_in_open:
                #add it to open
                ol.append(DijkHeap(new[0], (new[1] + element.getDist()), element))
            elif new_element_already_in_open:
                #check if this is better option
                if new[1] + element.getDist() < existing_in_open.getDist():
                    ol.append(DijkHeap(new[0], (new[1] + element.getDist()), element))

        if self.debug: print("All open elements: %s" % ol)
        if self.debug: print("All closed elements: %s" % cl)
        if self.debug: print()
        ch = self.choose_cheapest_from_openlist(ol, cl)
        return self.expand(ch, ol, cl)


    def choose_cheapest_from_openlist(self, ol, cl):
        if len(ol) > 0:
            # Getting first unexpanded
            tmp = ol[0]
            # Getting better option
            for element_open in ol:
                in_closed = False
                if (element_open.getDist() < tmp.getDist()):
                    for element_closed in cl:
                        if element_open.vert == element_closed.vert:
                            in_closed = True
                    if not in_closed:
                        tmp = element_open
        else:
            print("ERROR: Open List is empty")
            return False
        return tmp

    def run_old(self, frm, to):
        if frm == to:
            return[[0],frm]
        self.openList = []
        self.closedList = []
        self.debug = False
        #if frm==to: return [[0]]
        self.openList = []
        self.closedList = []
        self.fromto = [frm, to]
        # Starting with departure Vertex
        self.openList.append(DijkHeap(self.fromto[0], 0))
        dist = self.expand(self.openList[0])
        # Loop (while not found, determine the next chosen one)
        dist = False
        while not dist:
            dist = self.expand(self.choose_cheapest_from_openlist())
        return dist

    def expand_old(self, element):
        #Todo heres the bug
        self.openList.remove(element)
        self.closedList.append(element)
        # IF found destination, trace back the path
        if (element.getID() == self.fromto[1] and len(self.closedList)!=1) or (element.getID() == self.fromto[0] and len(self.closedList)>1):
            if self.debug: print("FOUND DESTINATION! From %d to %d, distance = %d"%(self.fromto[0], self.fromto[1], element.getDist()))
            path = []
            current = element
            while current is not None:
                path.append(current.getID())
                current = current.parent
            path.append([element.getDist()])
            return path[::-1]  # Return reversed path
        # creating list of neighbors to expand
        nextPushesList = list(self.map.get_station(element.getID()).get_connections().items())
        if self.debug: print("Next to expand: %s, its Neighbors: %s" % (element, nextPushesList))

        for new in nextPushesList:
            loop_found = False
            new_in_closed = True
            new_in_open = True
            existing_in_open = None
            for closed in self.closedList:
                if new[0] == closed.getID():
                    new_in_closed = False
            if new[0] == self.fromto[0]:
                loop_found = True
            for open in self.openList:
                if new[0] == open.getID():
                    new_in_open = False
                    existing_in_open = open
            if loop_found:
                self.openList.append(DijkHeap(new[0], (new[1] + element.getDist()), element))
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

    def choose_cheapest_from_openlist_old(self):
        if len(self.openList)>0:
            # Getting first unexpanded
            tmp = self.openList[0]
            # Getting better option
            for element_open in self.openList:
                in_closed = False
                if (element_open.getDist() < tmp.getDist()) and (not in_closed):
                    for element_closed in self.closedList:
                        if element_open.vert == element_closed.vert:
                            in_closed = True
                    if not in_closed:
                        tmp = element_open
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
        return ("V%d:%i" % (self.vert, self.dist))