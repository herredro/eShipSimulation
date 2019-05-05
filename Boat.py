import Global as G
from Algorithms import Strategies


class Boat:
    # Boat specific variables
    def __init__(self, sim, id, location, battery = 100, capacity = 10, charging_speed = 1, consumption = 1):
        self.sim = sim
        self.id = ("B" + str(id))
        self.location = location
        self.capacity = capacity
        self.occupied = 0
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
#        self.dijk = Strategies.Dijkstra(self.sim.map)
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))

    # Method to actually move a boat to a given station
    def drive(self, stop):
        old_loc = self.get_location()
        new_loc = stop
        # check if edge to new_loc is existing
        if old_loc.isConnectedTo(new_loc):
            distance = old_loc.get_distance(new_loc)
            bat = self.get_battery()
            # Check if battery sufficient. If yes: move.
            if self.drivable__battery(distance):
                # move
                self.get_location().remove_visitor(self)
                self.discharge(distance)
                #Todo Simpy: self.sim.env.timeout(distance)
                new_loc.add_visitor(self)
                self.set_location(new_loc)
                if G.debug: print("--> Boat %s drove to Station %s. Battery at %s\n" % (
                self.get_id(), self.get_location(), self.get_battery()))
                return True
            else:
                print("ERROR Battery:\tCannot drive to any more station. Battery capacity too low.")
                return False
        else:
            path = self.sim.map.dijk.run(old_loc.get_id(), new_loc.get_id())
            if path == 0:
                print("WARNING dijk:\t%s staying at same place"%str(self))
                return False
            print("WARN. Drive():\tno direct path. Jumping with:", path)
            if type(path)==list:
                if self.drivable__battery(path[0][0]):
                    for nextS in path[2:]:
                        self.drive(self.sim.map.get_station_object(nextS))
                        return True
                else: print("ERROR Battery:\tNot enough for desired path")

    def pickup(self, amount):
        if self.location.demand > 0:
            space_left = self.capacity - self.occupied
            if amount == 'max':
                if self.location.demand >= space_left:
                    self.occupied = self.capacity
                    self.location.demand -= space_left
                elif self.location.demand < space_left:
                    self.occupied = self.location.demand
                    self.location.demand = 0
            else:
                amount = int(amount)
                if amount > space_left:
                    self.occupied = space_left
                    self.location.demand -= space_left
                    print("Picked up (only) %s" %space_left)
                else:
                    self.occupied += amount
                    self.location.demand -= amount
        else: print("WARNING Pickup:\t%s has nothing to pick up at %s" % (str(self), str(self.location)))

    def dropoff(self, amount):
        if self.occupied > 0:
            if amount == 'max':
                self.occupied = 0
                print("ACTION Dropoff:\t%s dropped of %s passengers" % (str(self), self.occupied))
            elif int(amount) > self.occupied:
                self.occupied = 0
                print("WARNING Dropoff:\tonly had %s to drop off (not %s)" %(self.occupied, amount))
            elif int(amount) <= self.occupied:
                self.occupied -= int(amount)
                print("ACTION:\t%s dropped off %s. Left with: %s" % (self, amount, self.occupied))
        else: print("ERROR Dropoff:\t%s has nothing to drop off" %str(self))

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

    # Boat initializes its charging procedure


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
