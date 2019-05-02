import Network as Net
import Boat as Bo
import Strategies
import Global as G
from tabulate import tabulate

# Controller for Map and Boats. While Map and Boat classes provide basic functionality,
# the controller takes care of decisions and actions such as creation and movements

# SIMPY

class Maps:
    # Map controller has an instance of map
    def __init__(self):
        self.map = Net.Graph()
        #self.chargers = {}

    def create_inital_map(self, edgeList=G.edgeList):
        for i in edgeList:
            try:
                if i[3] == 1:
                    # Todo: if charger was vertex, it looses existing edges when transformed to charger
                    self.map.addcharger(i[0])
            except IndexError:
                pass
            self.map.add_edge(i[0], i[1], i[2])
        # Todo Stations are sorted by edge-creation, not by actual station number
        self.printedges_tabulate()

    # Printing all edges visually
    def printedges_tabulate(self):
        tabs = []
        # vid = None
        # wid = None
        # dis = None
        for v in self.map.get_all_stations():
            for w in v.get_connections():
                vid = "S" + str(v.get_id())
                wid = "S" + str(w)
                dis = v.get_dist_fromID(w)
                tabs.append([vid, wid, dis])
        #print("---------EDGES----------")
        print("EDGES:")
        print(tabulate(tabs, headers=['From', 'To', 'Distance'], tablefmt="fancy_grid"))
        #print("------------------------\n")

class Boats:
    # Boat Controller has map, number of boats, boats themselves as dictionary
    def __init__(self, map):
        self.map = map
        self.numBoats = 0
        self.boats = {}
        # ToDo decide: static or instance?
        self.move_strategy = Strategies.Strategies(self.map)

    # Creates a Boat and adds to boat dict.
    def new_boat(self, id, loc=-1, bat=100, chsp=1, cons=1):
        # default location -1 means to position boat at start-vertex
        if loc == -1:
            loc = self.map.get_station_object(G.startVertex)
        boat = Bo.Boat(id, loc, bat, chsp, cons)
        self.boats[id] = boat
        # location needs to know it has new visitor
        loc.add_visitor(boat)
        self.numBoats += 1

    # Method to create several basic boats at once
    def create_basic_boats(self, numBoats2create=G.numBoats):
        for i in range(self.numBoats+1, self.numBoats+numBoats2create+1):
            boat = Bo.Boat(id=(str(i)), location=self.map.get_station_object(1))
            self.boats[i] = boat
            self.map.get_station_object(1).add_visitor(boat)
            self.numBoats = self.numBoats + 1

    # Method (loop) that asks user which boat to move
    def move_boat__input(self):
        self.printmapstate()
        self.printboatlist()
        print("Which Boat to move (x to cancel)? Possible boats are: ", end='')
        for boat in self.boats.keys():
            print(boat, sep='', end=', ', flush=True)
        choice = input("Enter Boatnumber: ")
        if choice == "x":
            print("CANCELED\n")
        else:
            try:
                choice = int(choice)
                boat = self.boats[choice]
                self.move_station__input(boat)
            except Exception:
                print("ERROR: wrong input\n")
                self.move_boat__input()

    def move_station_algorithm(self, boat, destination, algo):
        if algo=="d":
            Strategies.Dijkstra.getPath(self.map, boat.get_location(), destination)


    # Method (loop) that asks user where to move to or charge a given boat
    def move_station__input(self, boat):
        print("\n\n\n\n")
        self.printboatlist()
        self.printmapstate()
        print("Enter next station for %s(%s%%) at S%s. Adjacent stations are: " %(boat.get_id(), boat.get_battery(), boat.get_location().get_id()) + str(boat.get_location().get_connections()) + ", {station: distance}")

        choice = input("Enter Strategy:\n1-9 = Station X\nc\t= closest (algorithm)\ne\t= charge\nx\t= cancel. Your input: ")
        # Choice: Move to closest station.
        if choice == "c":
            to = Strategies.Strategies.closest_neighbor(self.map, boat)
            self.drive(boat, to)
            self.move_station__input(boat)
        # Choice: Cancel.
        elif choice == "x":
            print("CANCELED\n")
            self.move_boat__input()
        # Choice: Charge.
        elif choice == "e":
            if type(boat.get_location()) == Net.Charger:
                # Todo charge max
                duration = input("How long should boat charge? (type 'max' for full charge)")
                if duration == "max":
                    boat.get_location().serve(boat, -1)
                else:
                    boat.get_location().serve(boat, int(duration))
                self.move_station__input(boat)
            else:
                print("ERROR CHARGE: Boat not at charger")
                self.move_station__input(boat)
        # Choice: Move to specific Station.
        else:
            # Check if user-specified location is in range (i.e. edge existing)
            try:
                choice_int = int(choice)
                to = self.map.get_station_object(choice_int)
                self.drive(boat, to)
                self.move_station__input(boat)
            except Exception:
                print("ERROR: wrong input\n")
                self.move_station__input(boat)

    # Method to actually move a boat to a given station
    def drive(self, boat, stop):
        old_loc = boat.get_location()
        new_loc = stop
        # check if edge to new_loc is existing
        # Todo Implement: Path should exist even though there is no direct edge
        if old_loc.isConnectedTo(new_loc):
            distance = old_loc.get_distance(new_loc)
            bat = boat.get_battery()
            # Check if battery sufficient. If yes: move.
            if self.drivable__battery(boat, distance):
                #move
                boat.get_location().remove_visitor(boat)
                #self.map.get_if_stop(stop).add_visitor(boat)
                new_loc.add_visitor(boat)
                boat.set_location(new_loc)
                boat.discharge(distance)
                print("--> Boat %s drove to Station %s. Battery at %s\n" % (boat.get_id(), boat.get_location(), boat.get_battery()))
            else:
                print("Cannot drive to any more station. Battery capacity too low.")
        else: print("There is no path to this Station")

    # Method to check if distance is doable with battery load
    def drivable__battery(self, boat, distance):
        if (boat.get_battery() - (distance * boat.get_consumption())) > 0: return True
        else: return False

    # Prints map state (i.e. which boat is where)
    def printmapstate(self):
        print("STATIONS:")
        #print(self.map.get_network_matrix())
        check = self.map.get_network_tabulate()
        print(tabulate(check, tablefmt="fancy_grid"))

    # Prints list of boats including their specs
    def printboatlist(self):
        tabs = []
        for b in self.boats.values():
            id = b.get_id()
            loc = b.get_location().get_id()
            bat = str(b.get_battery()) + "%"
            chs = b.get_charging_speed()
            con = b.get_consumption()
            tabs.append([id, loc, bat, chs, con])
        print("BOATS:")
        print(tabulate(tabs, headers=['ID', 'Location', 'Battery', 'Ch.Spd.', 'Cons.'], tablefmt="fancy_grid"))
