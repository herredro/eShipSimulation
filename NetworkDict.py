from tabulate import tabulate

class Station:
    def __init__(self, id):
        self.id = id
        self.adjacent = {}
        self.visitor = []

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent

    def isConnectedTo(self, station):
        id = station.get_id()
        if id in self.adjacent:
            return True
        else: return False

    def get_next_stop(self):
        return self.adjacent.values()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return int(self.adjacent[neighbor.get_id()])

    def get_distance(self, neighbor):
        #ToDo Figure out how to avoid non-existing path
        try:
            distance = int(self.adjacent[neighbor.get_id()])
        except Exception:
            print()
        return distance

    def get_dist_fromID(self, neighborID):
        return int(self.adjacent[neighborID])

    def add_visitor(self, boat):
        self.visitor.append(boat)

    def remove_visitor(self, boat):
        self.visitor.remove(boat)

    def get_visitors(self):
        return self.visitor

    # def __str__(self):
    #     return 'Station' + str(self.id) + ' has route to: ' \
    #            + str([x.id for x in self.adjacent]) + ' with distance ' \
    #            + str([self.get_weight(x) for x in self.adjacent])

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return "Station " + str(self.id)


class Graph:
    def __init__(self):
        self.stops = {}
        self.chargers = {}
        self.num_stations = 0
        self.num_chargers = 0

    def __iter__(self):
        return iter(self.stops.values())

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.stops:
            self.addstation(frm)
        if to not in self.stops:
            self.addstation(to)

        self.stops[frm].add_neighbor(to, cost)
        #self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def addstation(self, node):
        self.num_stations = self.num_stations + 1
        new_vertex = Station(node)
        self.stops[node] = new_vertex
        return new_vertex

    def addcharger(self, node, atStation):
        # Charger is not a vertex
        #self.num_vertices = self.num_vertices + 1
        new_charger = Charger(node, atStation)
        self.stops[node] = new_charger
        return new_charger

    def get_if_stop(self, n):
        if n in self.stops:
            return self.stops[n]
        else:
            print("ERROR NEW LOCATION NOT EXISTING")
            return None

    def get_closest_stop(self, start):
        options = start.get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = self.get_if_stop(closest_tuple[0][0])
        return closest_stop

    def get_stop_dict(self):
        return self.stops

    def get_stop_object(self):
        return self.stops.values()

    def get_mat_old(self):
        mat = []
        for x in self.stops.values():
            mat.append(x.get_visitors())
        return mat

    def get_mat(self):
        mat = ""
        for x in self.stops.values():
            visitors = x.get_visitors()
            if type(x) is Charger:
                mat += "%s:[*" % (x)
                for y in visitors:
                    mat += "%s " % (y)
                mat += "]\t"
            elif type(x) is Station:
                mat += "%s:[" % (x)
                for y in visitors:
                    mat += "%s" % (y)
                mat += "]\t"
        return(mat)

    def print_mat_old(self):
        mat = []
        for x in self.stops.values():
            mat.append(x.get_visitors())
        print(mat)

    def print_mat(self):
        mat = ""
        for x in self.stops.values():
            visitors = x.get_visitors()
            if type(x) is Charger:
                mat += "%s[*" % (x)
                for y in visitors:
                    mat += "%s" % (y)
                mat += "]\t"
            elif type(x) is Station:
                mat += "%s[" % (x)
                for y in visitors:
                    mat += "%s" % (y)
                mat += "]\t"
        print(mat)

    def get_network(self):
        for v in self.get_stop_object():
            for w in v.get_connections():
                vid = v.get_id()
                wid = w
                print('\t\t%s,%s,%3d' % (vid, wid, v.get_dist_fromID(w)))


    def get_distance(self, a, b):
        return a.get_dist_fromID(b)


class Charger(Station):

    def __init__(self, id, atStation):
        # Necessary Vertex inits
        super().__init__(id)
        self.add_neighbor(atStation, 1)
        # Charger inits
        self.fromStation = atStation
        self.occupiedBy = None
        self.energyConsumed = 0

    def charge(self, boat):
        if (self.occupiedBy == None): print("ERROR CHARGER: Cannot charge when no boat docked")
        if (self.occupiedBy == boat):
            while (self.occupiedBy.get_battery() < 100):
                self.occupiedBy.charge(1)
            print("Boat %s fully charged" % (str(boat.get_id())))
        else:
            print("ERROR CHARGER: Charger already occupied")

    def dock(self, boat, charger):
        charger.occupiedBy = boat
        charger.occupiedBy.set_location(charger)

    def undock(self, charger):
        if charger.occupiedBy is None:
            print("ERROR CHARGER: Dock undocking: Dock already Empty")
        else:
            charger.occupiedBy.set_location = charger.fromStation
            charger.occupiedBy = None

    def charge(self, boat, charger):
        self.dock(boat, charger)
        charger.charge(boat)
        self.undock(charger)

    def getstation(self):
        return self.fromStation