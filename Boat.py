import Global as G
from Algorithms import Strategies
from Network import Station
from colorama import Fore, Back, Style
import logging


logging.basicConfig(level=logging.INFO, filemode="w", filename="test.log", format="%(levelname)s - %(funcName)s - %(message)s\n")
log_pickdrop = logging.getLogger("Pick/Drop")


class Boat:
    # Boat specific variables
    def __init__(self, sim, id, location, battery = 100, capacity = 10, charging_speed = 1, consumption = 1):
        self.sim = sim
        self.id = ("B" + str(id))
        self.location = location
        self.capacity = capacity
        self.passengers = []
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        self.idle = True
#        self.dijk = Strategies.Dijkstra(self.sim.map)
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))

    def drive(self, stop):
        self.idle = 0
        self.old_loc = self.get_location()
        if type(stop) == int:
            self.new_loc = self.sim.map.get_station_object(stop)
        else: self.new_loc = stop
        distance = self.sim.map.get_distance(self.old_loc, self.new_loc)
        if self.drivable__battery(distance):
            self.old_loc.remove_visitor(self)
            self.set_location(self.new_loc)
            self.discharge(distance)
            print(Fore.BLACK + Back.GREEN + "SIMPY t=%s: %s started driving to %s" % (self.sim.env.now, str(self), str(stop)), end='')
            print(Style.RESET_ALL)
            yield self.sim.env.timeout(distance)
            self.idle = 1
            print(Fore.BLACK + Back.GREEN + "SIMPY t=%s: %s arrived at %s" % (self.sim.env.now, str(self), str(stop)), end='')
            print(Style.RESET_ALL)
            self.new_loc.add_visitor(self)
            return True
        else:
            print("ERROR Battery:\tCannot drive to any more station. Battery capacity too low.")
            return False

    def pickup(self, amount):
        if self.location.get_demand() > 0:
            space_left = self.capacity - len(self.passengers)
            for passenger in self.location.get_passengers(space_left):
                self.passengers.append(passenger)
            if amount > space_left:
                logging.info("%s:\t%s picked up (only) %s at station %s" % (self.sim.env.now, str(self), space_left, str(self.location)))
            else: logging.info("%s:\tPicked up %s" % (self.sim.env.now, space_left))
        else: logging.warning("%s:\t%s has nothing to pick up at %s" % (self.sim.env.now, str(self), str(self.location)))


    def dropoff(self, amount):
        if len(self.passengers) > 0:
            if amount > len(self.passengers):
                logging.info("%s:\t%s dropped off (only) %s (not %s)" % (self.sim.env.now, str(self), len(self.passengers), amount))
                self.passengers = []
            else:
                # dropoff #amount passengers
                for i in range(amount):
                    self.passengers.pop(0)
                logging.info("%s:\t%s dropped off %s. Left with: %s" % (self.sim.env.now, self, amount, len(self.passengers)))
        else: logging.warning("%s:\t%s has nothing to drop off" %(self.sim.env.now, str(self)))

    def charge(self, time):
        if (self.battery + (time * self.charging_speed)) > 100:
            self.battery = 100
            return 100
        else:
            self.battery = self.battery + (time * self.charging_speed)
            return self.battery

    # Method to check if distance is doable with battery load
    def drivable__battery(self,  distance):
        if (self.get_battery() - (distance * self.get_consumption())) > 0: return True
        else: return False

    def set_location(self, loc):
        self.location = loc

    def get_location(self):
        return self.location

    # Boat knows its battery status
    def get_battery(self):
        return self.battery

    def get_battery__print(self):
        print("\t...BATTERY Boat %s: %d%%" % (self.id, self.battery))

    # Boat looses battery
    def discharge(self, minus):
        self.battery = self.battery - (minus * self.consumption)

    # Boat has a consumption
    def get_consumption(self):
        return self.consumption

    # Boat has an ID
    def get_id(self):
        return self.id

    # Boat has a charging speed
    def get_charging_speed(self):
        return self.charging_speed

    def toString(self):
        return print("\t...This is Boat %s with \n\t\tbattery=%s, charging_speed=%s, consumption=%s\n" % (
            self.id, self.battery, self.charging_speed, self.consumption))

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)
