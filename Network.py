import Global as G
import Algorithms.Dijkstra
import Passengers
from colorama import Fore, Back, Style
from tabulate import tabulate
import logging
import simpy
import random
import math
from numpy import random as nprandom
random.seed(G.randomseed)
nprandom.seed(G.randomseed)
# ToDo should everybody know MAP? i.e. should Station know map? Maybe better for Multi Agent Algorithm


# Todo Comment
class Graph:
    # Graph has list of stations (vertex pbject) and list of chargers (charger object)
    def __init__(self, sim = None, num_stations=G.num_stations, dist_mean=G.dist_mean, dist_std=G.dist_std):
        self.sim = sim
        self.params = sim.params
        self.env = sim.env
        self.stations = {}
        self.distances = {}
        self.between = {}
        self.chargers = {}
        self.num_stations = 0
        self.num_chargers = 0
        self.dijk = Algorithms.Dijkstra.Dijk(self)

        if num_stations == 0:
            self.create_map(self.sim.params.edges)
        else:
            self.create_map(self.map_creator(num_stations, dist_mean, dist_std))
        self.init_demand()
        #self.append_initial_demand(self.generate_initial_demand())

    def create_distance_matrix(self):
        for station in self.stations.values():
            self.distances[station] = {}
        for station_from in self.stations.values():
            self.between[station_from] = {}
            for station_to in self.stations.values():
                self.distances[station_from][station_to] = self.get_distance(station_from, station_to)
                self.between[station_from][station_to] = {}

    def demand_left(self):
        for station in self.stations.values():
            if station.get_demand() > 0:
                return True
        return False

    def map_creator(self, num_stations, distance_mean, distance_std):
        map = []
        for i in range(num_stations):
            frm = i + 1
            to = i + 2 if i < num_stations - 1 else 1
            dist = int(math.sqrt(random.gauss(distance_mean, distance_std)) ** 2)
            map.append([frm, to, dist])
        return map



    # Todo Demand: needs to be drawn from distribution
    def create_map(self, edgeList=G.edgeList):
        for i in edgeList:
            try:
                if i[3] == 1:
                    # Todo: if charger was vertex, it looses existing edges when transformed to charger
                    self.add_charger(i[0])
            except IndexError:
                pass
            self.add_edge(i[0], i[1], i[2])
        # Todo Stations are sorted by edge-creation, not by actual station number
        self.create_distance_matrix()
        if G.map: self.printedges_tabulate()

    def init_demand(self):
        self.stationkeys = []
        for stationkey in self.stations.keys():
            self.stationkeys.append(stationkey)

        for station in self.stations.values():
            station.init_demand(Passengers.Passengers(self, station, self.stationkeys))

    def generate_initial_demand(self):
        nprandom.seed(G.randomseed)
        random.seed(G.randomseed)
        self.poisson_arrivals_expected = []
        for i in range(len(self.params.expected_arrivals)):
            self.poisson_arrivals_expected.append(self.params.expected_arrivals[i])
        self.poisson_arrivals = []
        for i in range(len(self.params.expected_arrivals)):
            station = []
            for i in range(len(self.params.expected_arrivals)):
                for j in range(int(G.SIMTIME / G.INTERARRIVALTIME)):
                    station.append(nprandom.poisson(self.poisson_arrivals_expected[i]))
                self.poisson_arrivals.append(station)
        return self.poisson_arrivals_expected

    def append_initial_demand(self, num):
        i = 0
        for station in self.stations.values():
            station.passengers.add_multiple_demand(num[i], arrivaltime=self.env.now)
            i+=1

    def update_demand(self):
        for station in self.stations.values():
            pass

    def demand_left(self, station = False):
        if station is False:
            for station in self.stations:
                if len(station.passengers.passengers) > 1:
                    return True
            return False
        else:
            if len(station.passengers.passengers) > 1:
                return True
            return False

    def __iter__(self):
        return iter(self.stations.values())

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.stations:
            self.add_station(frm)
        if to not in self.stations:
            self.add_station(to)
        self.stations[frm].add_neighbor(to, cost)
        self.stations[to].add_neighbor(frm, cost)

    # Todo Maybe: move to Controller?
    def add_station(self, node):
        self.num_stations = self.num_stations + 1
        new_vertex = Station(node, self.sim)
        self.stations[node] = new_vertex
        return new_vertex

    def add_charger(self, node):
        # Charger is not a vertex
        #self.num_vertices = self.num_vertices + 1
        new_charger = Charger(node, self.sim)
        self.stations[node] = new_charger
        self.chargers[node] = new_charger
        return new_charger

    def get_all_stations(self):
        return list(self.stations.values())

    # Input: Integer Return: Object
    def get_station(self, n):
        if n in self.stations:
            return self.stations[n]
        else:
            print("ERROR: new location not existing")
            logging.error("new location not existing")
            return False

    def get_in_between(self, a0, b0):
        a = self.get_station(a0)
        b = self.get_station(b0)
        if self.between[a][b] == {}:
            between = self.dijk.run(a0, b0)[1:][1:-1]
            if len(between ) > 1:
                print("IN BETWEEENN PROOOOOOOOBELMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
            elif between == []:
                self.between[a][b] = None
            else:
                self.between[a][b] = between
        return self.between[a][b]

    def get_distance(self, a, b):
        if a == b: return 0
        elif a.is_connected_to(b):
            distance = int(a.adjacent[b.get_id()])
        else:
            distance = self.dijk.run(a.get_id(), b.get_id())[0][0]
        return distance

    def get_distance_id(self, a, b):
        return self.get_distance(self.get_station(a), self.get_station(b))

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
        return mat

    def get_network_tabulate(self):
        stationnames = []
        boats = []
        total = []
        # Todo Demand: update for new demand
        for stationnum in self.stations.keys():
            if type(self.stations[stationnum]) == Charger:
                stationnames.append("⚡S%s:%i" % (stationnum, self.stations[stationnum].get_demand()))
            else:
                stationnames.append("S%s:%i" %(stationnum, self.stations[stationnum].get_demand()))
            boatlist = self.stations[stationnum].get_visitors()
            boatshere = []
            for boat in boatlist:
                if boat.idle:
                    boatshere.append("(%s)" %(boat))
                else:
                    boatshere.append("%s" %(boat))
            boats.append(boatshere)
        total.append(stationnames)
        total.append(boats)
        return total

    def printmapstate(self):
        print("\nSTATIONS:")
        #print(self.map.get_network_matrix())
        check = self.get_network_tabulate()
        print(tabulate(check, tablefmt="fancy_grid"))

    def printedges_tabulate(self):
        tabs = []
        for v in self.get_all_stations():
            for w in v.get_connections():
                vid = "S" + str(v.get_id())
                wid = "S" + str(w)
                dis = self.distances[v][self.get_station(w)]
                tabs.append([vid, wid, dis])
        #print("---------EDGES----------")
        print("EDGES:")
        print(tabulate(tabs, headers=['From', 'To', 'Distance'], tablefmt="fancy_grid"))
        #print("------------------------\n")


# Class for basic Station (i.e. not a charger)
class Station:
    # Station knows its adjacent stations and boats that are present
    def __init__(self, id, sim):
        self.id = id
        self.sim = sim
        self.adjacent = {}
        self.boats = []
        self.demand = 0

    # Method to add an adjacent station
    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def init_demand(self, passengers_object):
        self.passengers = passengers_object
        self.sim.env.process(self.passengers.update_poisson())

    def get_demand(self):
        return len(self.passengers.passengers)

    # Todo Method to delete occurences in allPassengers (if pas. are taken)
    def get_num_demand_to(self, stationnum):
        demand_to = 0
        for passenger in self.passengers.passengers:
            if passenger.dest == stationnum:
                demand_to +=1
        return demand_to

    def get_demand_to(self, station, amount):
        pas = []
        for passenger in self.passengers.passengers:
            if passenger.dest == station.id:
                pas.append(passenger)
        pas = pas[:amount]
        for pa in pas:
            self.passengers.passengers.remove(pa)
        return pas

    def get_passengers(self, amount):
        passengers_boarding = []
        # Todo Demand: Implement for amount<passengers_available
        for i in range(amount):
            try:
                passengers_boarding.append(self.passengers.passengers.pop(0))
            except IndexError as e:
                logging.warning("WARNING nothing to board")
        return passengers_boarding

    # def get_passengers_to(self, stationnum, amount):
    #     passengers_boarding = []
    #     for i in amount:
    #         if passenger.dest == stationnum:
    #             passengers_boarding.append(self.passengers.passengers.pop(0))
    #     return passengers_boarding

    def remove_demand(amount):
        pass

    # Return: all adjacent stations as a dictionary
    def get_connections(self):
        return self.adjacent

    # Boolean: True if both stations are adjacent
    def is_connected_to(self, station):
        id = station.get_id()
        if id in self.adjacent:
            return True
        else: return False

    # Return: ID of this station
    def get_id(self):
        return self.id

    # Method for station to know it has a new visitor (boat)
    def add_visitor(self, boat):
        self.boats.append(boat)
        try:
            self.sim.stats.visited_stations[boat][self] += 1
        except KeyError:
            pass

    # Method for station to know a boat has left
    def remove_visitor(self, boat):
        self.boats.remove(boat)

    # Return: All boats at this station
    def get_visitors(self):
        return self.boats

    def __repr__(self):
        return "S%s" % (str(self.id))

    def __str__(self):
        return "S%s:%i" % (str(self.id), self.get_demand())


class Charger(Station):

    # Charger is subclass of Vertex with additional charging functionality
    def __init__(self, id, sim):
        # Necessary Vertex inits
        super().__init__(id, sim)
        self.env = sim.env
        # Charger inits:
        # means the charging spot at this station is occupied by "None/BoatX"
        self.occupiedBy = None
        # counting all energy that charger transfered to boats
        self.energyConsumed = 0
        self.resource = simpy.Resource(self.env, capacity=1)

    # Boat can be at Charger but since Charger is a Station too, serve() needs to be called to process charging
    def serve(self, boat, chargeNeeded):

        with self.resource.request() as req:
            yield req
            if G.d_charge:
                print(Fore.BLACK + Back.LIGHTYELLOW_EX + "%s:\t%s   \tCHARGE START @%s" % (self.env.now, str(boat), str(self)), end='')
                print(Style.RESET_ALL)
            self.sim.stats.charger_usage_in_time[self][self.env.now-1] = 0
            self.sim.stats.charger_usage_in_time[self][self.env.now] = 1
            self.dock(boat)
            oldbat = boat.get_battery()
            if (self.occupiedBy == None):
                if G.d_charge: print("ERROR CHARGER: Cannot serve when no boat docked")
                logging.error("ERROR CHARGER: Cannot serve when no boat docked")
            if (self.occupiedBy == boat):
                # if (chargeNeeded == -1) or (chargeNeeded > 100-boat.get_battery()):

                current_bat = boat.get_battery()
                chargeNeeded = G.BATTERY - current_bat
                # Todo Charge: Realistic timeout
                charge = self.env.process(boat.charge(chargeNeeded))
                # else:
                #     self.env.process(boat.charge(chargeNeeded))
                self.energyConsumed += chargeNeeded

                yield charge
                new_battery = boat.get_battery()
                if G.d_charge:
                    print(Fore.BLACK + Back.YELLOW + "%s:\t%s   \tCHARGE STOP  @%s (%d%%-%d%%)" % (self.env.now, str(boat), str(self), current_bat, new_battery), end='')
                    print(Style.RESET_ALL)
                self.undock()
                self.sim.stats.charger_usage_in_time[self][self.env.now - 1] = 1
                self.sim.stats.charger_usage_in_time[self][self.env.now] = 0
            else:
                print("ERROR CHARGER: Charger already occupied")

            # yield self.env.timeout(int(chargeNeeded/boat.charging_speed))

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

    def __repr__(self):
        return "C%s" % (str(self.id))

    def __str__(self):
        return "C%s:%i" % (str(self.id), self.get_demand())


