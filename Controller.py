import Network as Net
import Boat as Boat
from Algorithms import Strategies as Strategies
import Stats

import Global as G
from tabulate import tabulate
from colorama import Fore, Back, Style


# Controller for Boats. While the Boat class provides basic functionality,
# the controller takes care of decisions and actions such as creation and movements

class Boats:
    # Boat Controller has map, number of boats, boats themselves as dictionary
    def __init__(self, sim, mode, num=G.NUM_BOATS):
        self.sim = sim
        self.map = sim.map
        self.env = sim.env
        self.mode = mode
        self.numBoats = 0
        self.boats = {}
        self.map_strategy = Strategies.Strategies(self.map)
        Boat.Boat.count = 0
        self.create_basic_boats(num)

    def start_driving(self):
        if not self.mode:
            for boat in self.boats.values():
                # Anarchy
                self.sim.env.process(boat.strat.take())
        if self.mode:
            self.strategy = Strategies.Decision_Union(self.sim)
            for boat in self.boats.values():
                # Central
                self.env.process(self.strategy.take(self.boats[boat.id]))
        self.env.run(until=G.SIMTIME)






    # Creates a Boat and adds to boat dict.
    def new_boat(self, loc=G.locaction, bat=G.BATTERY, chsp=G.chargingspeed, cons=G.consumption):
        # default location -1 means to position boat at start-vertex
        if loc == -1:
            loc = self.map.get_station(G.startVertex)
        boat = Boat.Boat(self.sim, loc, battery=bat, charging_speed=chsp, consumption=cons)
        self.boats[boat.id] = boat
        # location needs to know it has new visitor
        loc.add_visitor(boat)
        self.numBoats += 1

    # Method to create several basic boats at once
    def create_basic_boats(self, numBoats2create, bat= G.BATTERY):
        for i in range(self.numBoats+1, self.numBoats+numBoats2create+1):
            boat = Boat.Boat(self.sim, location=self.map.get_station(1), battery=bat)
            self.boats[i] = boat
            self.map.get_station(1).add_visitor(boat)
            self.numBoats = self.numBoats + 1

    def sp_ui_boat_choice(self):
        #self.map.printmapstate()
        #self.printboatlist()
        print("Which Boat to move (x to cancel)? Possible boats are: ", end='')
        for boat in self.boats.keys():
            print(boat, sep='', end=', ', flush=True)
        choice = input("Enter Boatnumber: ")
        if choice == "x":
            print("CANCELED\n")
            pass
        else:
            try:
                choice = int(choice)
                boat = self.boats[choice]
                self.sp_destination_manual(boat)
            except Exception:
                print("ERROR: wrong input (choosing boat)\n")
                self.sp_ui_boat_choice()

    def sp_ui_fleet_destination(self):
        try:
            for boat in self.boats.keys():
                if self.boats[boat].idle:
                    self.sp_destination_manual(self.boats[boat])
        except Exception as e:
            print("ERROR simpy_destination: %s\n" % e)

    def sp_destination_manual(self, boat):
        self.printtime()
        self.printboatlist()
        self.map.printmapstate()
        print("Enter next station for %s(%s%%) at S%s. Adjacent stations are: " % (
        boat.get_id(), boat.get_battery(), boat.get_location().get_id()) + str(
            boat.get_location().get_connections()) + ", {station: distance}")

        choice = input("Enter Strategy:\n"
                       "1-9 = Station X\n"
                       "x\t= run_till_end. \nYour input: ")
        # Choice: Move to closest station.
        if choice == "x":
            self.env.run()
            self.map.printmapstate()
            pass
        # Choice: Move to specific Station.
        else:
            # Check if user-specified location is in range (i.e. edge existing)
            try:
                choice_int = int(choice)
                to = self.map.get_station(choice_int)
                #Simpy
                self.env.process(boat.take(to))
                self.env.step()
            except Exception:
                print("ERROR: wrong input for location\n")
                self.sp_destination_manual(boat)
        while not self.some_boat_idle():
            self.env.step()
        if self.env.peek() == self.env.now:
            self.env.step()
        self.sp_ui_fleet_destination()


    # Prints list of boats including their specs
    def printboatlist(self):
        tabs = []
        for b in self.boats.values():
            id = b.get_id()
            loc = str(b.get_location().get_id())
            if not b.idle: loc += " (soon)"
            bat = str(b.get_battery()) + "%"
            chs = b.get_charging_speed()
            con = b.get_consumption()
            tabs.append([id, loc, bat, chs, con])
        print("BOATS:")
        print(tabulate(tabs, headers=['ID', 'Location', 'Battery', 'Ch.Spd.', 'Cons.'], tablefmt="fancy_grid"))

    def printtime(self):
        print(Fore.BLACK + Back.LIGHTGREEN_EX + "t=%s" % (self.sim.env.now))
        print(Style.RESET_ALL)

    def some_boat_idle(self):
        self.some_idle = False
        for boat in self.boats.keys():
            if self.boats[boat].idle:
                self.some_idle = True
        return self.some_idle



    # OLD MOVEMENTS WITHOUT SIMPY
    def fleet_move_demand(self, strategy, pu_quant, do_quant):
        for boat in self.boats.values():
            nextstation = strategy(self.map, boat)
            boat.take(nextstation)
            boat.pickup_priorities(pu_quant)
            boat.dropoff(do_quant)
            self.map.update_demands()
            self.map.printmapstate()

    # Method (loop) that asks user which boat to move
    #Todo Q: Uses demand?
    def move_boat__input(self):
        self.map.printmapstate()
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
                print("ERROR: wrong input (choosing boat)\n")
                self.move_boat__input()

    # Method (loop) that asks user where to move to or charge a given boat
    def move_station__input(self, boat):
        print("\n\n\n\n")
        self.printboatlist()
        self.map.printmapstate()
        print("Enter next station for %s(%s%%) at S%s. Adjacent stations are: "
              %(boat.get_id(), boat.get_battery(), boat.get_location().get_id())
              + str(boat.get_location().get_connections()) + ", {station: distance}")


        choice = input("Enter Strategy:\n"
                       "1-9 = Station X\n"
                       "c\t= closest_station\n"
                       "h\t= highest_demand\n\n"
                       "p\t= pick up passengers\n"
                       "d\t= drop off passengers\n"
                       "e\t= charge\n"
                       "x\t= cancel. Your input: ")
        # Choice: Move to closest station.
        if choice == "c":
            to = Strategies.Strategies.closest_neighbor(self.map, boat)
            boat.take(to)
            self.move_station__input(boat)
        # Choice: Cancel.
        elif choice == "h":
            to = Strategies.Strategies.highest_demand(self.map, boat)
            boat.take(to)
            self.move_station__input(boat)
        elif choice == "p":
            amount = input("\nHow many passengers to pick up? ")
            boat.pickup_priorities(amount)
            self.move_station__input(boat)
        elif choice == "d":
            amount = input("\nHow many passengers to drop off? ")
            boat.dropoff(amount)
            self.move_station__input(boat)
        elif choice == "x":
            print("CANCELED\n")
            self.move_boat__input()
        # Choice: Charge.
        elif choice == "e":
            if type(boat.get_location()) == Net.Charger:
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
                to = self.map.get_station(choice_int)
                #self.drive(boat, to)
                boat.take(to)
                self.move_station__input(boat)
            except Exception:
                print("ERROR: wrong input for location\n")
                self.move_station__input(boat)
