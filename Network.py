from tabulate import tabulate
import Global as G
import Algorithms.Dijkstra
#ToDo should everybody know MAP? i.e. should Station know map? Maybe better for Multi Agent Algorithm

# Class for basic Station (i.e. not a charger)
class Station:
    # Station knows its adjacent stations and boats that are present
    def __init__(self, id):
        self.id = id
        self.adjacent = {}
        self.boats = []
        self.demand = 0


    def add_demand(self, num):
        self.demand = num

    # Method to add an adjacent station
    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    # Return: all adjacent stations as a dictionary
    def get_connections(self):
        return self.adjacent

    # Boolean: True if both stations are adjacent
    def isConnectedTo(self, station):
        id = station.get_id()
        if id in self.adjacent:
            return True
        else: return False

    # Return: ID of this station
    def get_id(self):
        return self.id

    # Return: Distance to a specified station
    def get_distance(self, neighbor):
        # ToDo Figure out how to avoid non-existing path
        try:
            distance = int(self.adjacent[neighbor.get_id()])
        # Todo more specific
        except Exception:
            print()
        return distance

    # Todo create one method ID_to_object and erase this method
    def get_dist_fromID(self, neighborID):
        return int(self.adjacent[neighborID])

    # Method for station to know it has a new visitor (boat)
    def add_visitor(self, boat):
        self.boats.append(boat)

    # Method for station to know a boat has left
    def remove_visitor(self, boat):
        self.boats.remove(boat)

    # Return: All boats at this station
    def get_visitors(self):
        return self.boats

    def __repr__(self):
        return "Station " + str(self.id)

    def __str__(self):
        return "Station " + str(self.id)
    # OLD:
    #     return 'Station' + str(self.id) + ' has route to: ' \
    #            + str([x.id for x in self.adjacent]) + ' with distance ' \
    #            + str([self.get_weight(x) for x in self.adjacent])

class Charger(Station):

    # Charger is subclass of Vertex with additional charging functionality
    def __init__(self, id):
        # Necessary Vertex inits
        super().__init__(id)
        # Charger inits:
        # means the charging spot at this station is occupied by "None/BoatX"
        self.occupiedBy = None
        # counting all energy that charger transfered to boats
        self.energyConsumed = 0

    # Boat can be at Charger but since Charger is a Station too, serve() needs to be called to process charging
    def serve(self, boat, chargeNeeded):
        self.dock(boat)
        oldbat = boat.get_battery()
        if (self.occupiedBy == None):
            print("ERROR CHARGER: Cannot serve when no boat docked")
        if (self.occupiedBy == boat):
            if (chargeNeeded == -1) or (chargeNeeded > 100-boat.get_battery()):
                current_bat = boat.get_battery()
                chargeNeeded = 100 - current_bat
                self.occupiedBy.charge(chargeNeeded)
            else:
                self.occupiedBy.charge(int(chargeNeeded))
            self.energyConsumed += chargeNeeded
            print("Boat %s charged +%d (from %d%% to %d%%)" % (str(boat.get_id()), (boat.get_charging_speed() * chargeNeeded), oldbat, boat.get_battery()))
            self.undock()
        else:
            print("ERROR CHARGER: Charger already occupied")

    # Docking boat to the charger when it is already positioned at Charging Station
    def dock(self, boat):
        self.occupiedBy = boat
        boat.set_location(self)

    # Undock boat at charger. Boat remains at charger Vertex
    def undock(self):
        if self.occupiedBy is None:
            print("ERROR CHARGER: Dock undocking: Dock already Empty")
        else:
            self.occupiedBy = None

# Todo Comment
class Graph:
    #Graph has list of stations (vertex pbject) and list of chargers (charger object)
    def __init__(self, env):
        self.env = env
        self.stations = {}
        self.chargers = {}
        self.num_stations = 0
        self.num_chargers = 0

        self.dijk = Algorithms.Dijkstra.Dijk(self)

    def create_inital_map(self, edgeList=G.edgeList):
        for i in edgeList:
            try:
                if i[3] == 1:
                    # Todo: if charger was vertex, it looses existing edges when transformed to charger
                    self.add_charger(i[0])
            except IndexError:
                pass
            self.add_edge(i[0], i[1], i[2])
        # Todo Stations are sorted by edge-creation, not by actual station number
        self.printedges_tabulate()

    def __iter__(self):
        return iter(self.stations.values())

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.stations:
            self.add_station(frm)
        if to not in self.stations:
            self.add_station(to)
        self.stations[frm].add_neighbor(to, cost)

    #Todo Maybe: move to Controller?
    def add_station(self, node):
        self.num_stations = self.num_stations + 1
        new_vertex = Station(node)
        self.stations[node] = new_vertex
        return new_vertex

    def add_charger(self, node):
        # Charger is not a vertex
        #self.num_vertices = self.num_vertices + 1
        new_charger = Charger(node)
        self.stations[node] = new_charger
        self.chargers[node] = new_charger
        return new_charger

    def get_all_stations(self):
        return self.stations.values()

    # Input: Integer Return: Object
    def get_station_object(self, n):
        if n in self.stations:
            return self.stations[n]
        else:
            print("ERROR: new location not existing")
            return False

    def get_distance(self, a, b):
        return a.get_dist_fromID(b)

    #Todo function: update demand
    def update_demands(self):
        pass

    # PRINTS
    def get_network_string(self):
        mat = ""
        for x in self.stations.values():
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
    def get_network_tabulate(self):
        stationnames = []
        boats = []
        total = []
        for stationnum in self.stations.keys():
            if type(self.stations[stationnum]) == Charger:
                stationnames.append("⚡S%s:%i" % (stationnum, self.stations[stationnum].demand))
            else:
                stationnames.append("S%s:%i" %(stationnum, self.stations[stationnum].demand))
            boatlist = self.stations[stationnum].get_visitors()
            boatshere = []
            for boat in boatlist:
                boatshere.append("%s:%s" %(boat, boat.occupied))
            boats.append(boatshere)
        total.append(stationnames)
        total.append(boats)
        return total
    def printmapstate(self):
        print("STATIONS:")
        #print(self.map.get_network_matrix())
        check = self.get_network_tabulate()
        print(tabulate(check, tablefmt="fancy_grid"))
    def printedges_tabulate(self):
        tabs = []
        # vid = None
        # wid = None
        # dis = None
        for v in self.get_all_stations():
            for w in v.get_connections():
                vid = "S" + str(v.get_id())
                wid = "S" + str(w)
                dis = v.get_dist_fromID(w)
                tabs.append([vid, wid, dis])
        #print("---------EDGES----------")
        print("EDGES:")
        print(tabulate(tabs, headers=['From', 'To', 'Distance'], tablefmt="fancy_grid"))
        #print("------------------------\n")





