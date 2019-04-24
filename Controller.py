import NetworkDict as Net
import Boat as Bo
import Strategies
import Global as G
from tabulate import tabulate

class Map:
    def __init__(self):
        if G.debug: print("--STARTING MAP CONTROLLER--")
        self.map = Net.Graph()
        self.chargers = {}

    def get_map(self):
        return self.map

    def createBasic3(self):
        self.map.addstation(1)
        self.map.addstation(2)
        self.map.addstation(3)
        self.map.addcharger(9, 1)

        self.map.add_edge(1, 2, 10)
        self.map.add_edge(2, 3, 20)
        self.map.add_edge(3, 1, 50)

    def createBasic4Split(self):
        self.map.addstation(1)
        self.map.addstation(2)
        self.map.addstation(3)
        self.map.addstation(4)
        self.map.addcharger(9,1)

        self.map.add_edge(1, 2, 10)
        self.map.add_edge(1, 4, 5)
        self.map.add_edge(4, 2, 10)
        self.map.add_edge(2, 3, 20)
        self.map.add_edge(3, 1, 50)
        self.map.add_edge(1, 9, 20)
        self.map.add_edge(9, 1, 20)

    def printedges_tabulate(self):
        tabs = []
        vid = None
        wid = None
        dis = None
        for v in self.map.get_stop_object():
            for w in v.get_connections():
                vid = v.get_id()
                wid = w
                dis = v.get_dist_fromID(w)
                tabs.append([vid, wid, dis])
        #print("---------EDGES----------")
        print("EDGES:")
        print(tabulate(tabs, headers=['From', 'To', 'Distance'], tablefmt="fancy_grid"))
        #print("------------------------\n")

class Boats:
    def __init__(self, map):
        if G.debug: print("--STARTING BOAT CONTROLLER--")
        self.map = map
        self.numBoats = 0
        self.boats = {}
        self.move_strategist = Strategies.NextStop(self.map)

    def printstate__tabulate_OLD(self):
        state = self.map.get_mat()
        print("\t...Printing State\n\t" + "    " + state)

    def printstate_extended(self):
        print("STATIONS:")
        print(self.map.get_mat())
        print()

    def printboats_tabulate(self):
        # [[1,2,10], [1,4,5]]
        tabs = []
        # id = None
        # bat = None
        # chs = None
        # con = None
        for b in self.boats.values():
            id = b.get_id()
            loc = b.get_location().get_id()
            bat = b.get_battery()
            chs = b.get_charging_speed()
            con = b.get_consumption()
            tabs.append([id, loc, bat, chs, con])
        #print("---------------------BOATS---------------------")
        print("BOATS:")
        print(tabulate(tabs, headers=['ID', 'Location', 'Battery', 'Ch.Spd.', 'Cons.'], tablefmt="fancy_grid"))
        #print("-----------------------------------------------\n")

    def new_boat(self, id, loc=-1, bat=100, chsp=1, cons=1):
        if loc == -1:
            loc = self.map.get_if_stop(1)
        boat = Bo.Boat(id, loc, bat, chsp, cons)
        self.boats[id] = boat
        loc.add_visitor(boat)
        self.numBoats += 1

    def create_basic_boats(self, numBoats2create):
        for i in range(self.numBoats+1, self.numBoats+numBoats2create+1):
            boat = Bo.Boat(id=(str(i)), location=self.map.get_if_stop(1))
            self.boats[i] = boat
            self.map.get_if_stop(1).add_visitor(boat)
            self.numBoats = self.numBoats + 1

    def create_basic_boats2(self, numBoats2create):
        for i in range(self.numBoats, self.numBoats+numBoats2create):
            self.new_boat(id=("B"+str(i)))
            # boat = Bo.Boat(id=("B"+str(i)), location=self.map.get_if_stop(1))
            # self.boats[i] = boat
            # self.map.get_if_stop(1).add_visitor(boat)
            # self.numBoats = self.numBoats + 1

    def move_multiple__closest(self, boat, num):
        for i in range (0,num):
            to = self.map.get_closest_stop(boat.get_location())
            self.drive(self.boats[1], to)

    def move__inputboat(self):
        #ToDo print possible boats without dict_values()
        print("Which Boat to move (x to cancel)? Possible boats are: %s" %
              (
                  self.boats.values()
              ))
        choice = input("Enter Boatnumber: ")
        if choice == "x":
            print("CANCELED\n")
        else:
            try:
                choice = int(choice)
                boat = self.boats[choice]
                self.move__input(boat)
            except Exception:
                print("ERROR: wrong input\n")
                self.move__inputboat()

    def move__input(self, boat):
        print("--------------MAP STATE--------------")
        self.printstate_extended()
        print("-------------------------------------")
        print("Enter next station for Boat%s at Station%s. Adjacent stations are: " %(boat.get_id(), boat.get_location().get_id()) + str(boat.get_location().get_connections()))

        choice = input("Enter Strategy:\n1-9 = Station X\nc\t= closest (algorithm)\nx\t= cancel. Your input: ")
        if choice == "c":
            to = self.move_strategist.closest(boat)
            self.drive(boat, to)
            self.move__input(boat)
        elif choice == "x":
            print("CANCELED\n")
            self.move__inputboat()
        else:
            try:
                choice_int = int(choice)
                to = self.map.get_if_stop(choice_int)
                self.drive(boat, to)
                self.move__input(boat)
            except Exception:
                print("ERROR: wrong input\n")
                self.move__input(boat)

    def drivable__battery(self, boat, distance):
        if (boat.get_battery() - (distance * boat.get_consumption())) > 0: return True
        else: return False

    def drive(self, boat, stop):
        if G.debug: print(".BOAT DRIVING ALONE...")
        old_loc = boat.get_location()
        new_loc = stop
        if old_loc.isConnectedTo(new_loc):
            distance = old_loc.get_distance(new_loc)
            bat = boat.get_battery()
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