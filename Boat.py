import Global as G
from Algorithms import Strategies
from Network import Station
from colorama import Fore, Back, Style
import logging
import Algorithms.Strategies as Strat





class Boat:
    # Boat specific variables
    def __init__(self, sim, id, location, battery = 100, capacity = 10, charging_speed = 10, consumption = 1):
        self.sim = sim
        self.id = ("B" + str(id))
        self.location = location
        self.capacity = capacity
        self.passengers = []
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        self.idle = True
        self.strat = Strat.Decision(sim, self)
        self.sim.env.process(self.strat.take())

        #self.dijk = Strategies.Dijkstra(self.sim.map)
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))


    def drive(self, stop):
        #while True:
            # self.sim.cb.printtime()
            # self.sim.cb.printboatlist()
            # self.sim.map.printmapstate()
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
                logging.info("SIMPY t=%s: %s started driving to %s" % (self.sim.env.now, str(self), str(stop)))
                print(Fore.BLACK + Back.LIGHTYELLOW_EX + "SIMPY t=%s: %s started driving to %s" % (self.sim.env.now, str(self), str(stop)), end='')
                print(Style.RESET_ALL)
                yield self.sim.env.timeout(distance)
                self.idle = 1
                logging.info("SIMPY t=%s: %s arrived at %s" % (self.sim.env.now, str(self), str(stop)))
                print(Fore.BLACK + Back.GREEN + "SIMPY t=%s: %s arrived at %s" % (self.sim.env.now, str(self), str(stop)), end='')
                print(Style.RESET_ALL)
                self.new_loc.add_visitor(self)
                self.dropoff()
                self.pickup(self.capacity)
                #yield self.sim.env.process(self.pickup(10))
                #yield self.sim.env.process(self.dropoff(10))
                return distance
            else:
                print("ERROR Battery:\tCannot drive to any more station. Battery capacity too low.")
                return False

    def charge(self, charge_needed):
        #Todo Charge: implement 100 max
        self.idle = 0
        time = charge_needed / self.charging_speed
        yield self.sim.env.timeout(time)
        self.battery = self.battery + charge_needed
        self.idle = 1

    def pickup(self, amount, proc=None):
        #yield proc
        if self.location.get_demand() > 0:
            space_left = self.capacity - len(self.passengers)
            for passenger in self.location.get_passengers(space_left):
                self.passengers.append(passenger)
            if amount > space_left:
                if G.d_passenger: print("%s:\t%s PICKED (only) %s at station %s" % (self.sim.env.now, str(self), space_left, str(self.location)))
            else:
                if G.d_passenger: print("%s:\t%s PICKED %s at station %s" % (self.sim.env.now, str(self), space_left, str(self.location)))
        else:
            if G.d_passenger: print("%s:\t%s NO PICKUP cause no demand at %s" % (self.sim.env.now, str(self), str(self.location)))


    def dropoff(self):
        tobedropped = []
        for passenger in self.passengers:
            if passenger.dest == self.location.get_id():
                tobedropped.append(passenger)
        dropped = len(tobedropped)
        for passenger in tobedropped:
            self.passengers.remove(passenger)
        if G.d_passenger: print("%s:\t%s DROPPED %i passengers at %s"%(self.sim.env.now, str(self), dropped, self.location))




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
        if self.idle:
            return (str(self.id)+" @" + str(self.location))
        else:
            return (str(self.id) + " (@" + str(self.location)+")")

    def __str__(self):
        if self.idle:
            return "%s:%s" %(str(self.id), str(len(self.passengers)))
        else:
            return "%s:%s" % (str(self.id), str(len(self.passengers)))

    def __repr__(self):
        return str(self.id)
