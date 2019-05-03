import Global as G
class Boat:
    # Boat specific variables
    def __init__(self, sim, id, location, battery = 100, charging_speed = 1, consumption = 1):
        self.sim = sim
        self.id = ("B" + str(id))
        self.location = location
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))

    def sp_pursue_highest_demand(self):
        station = self.sim.cm.map.get_highest_demand()
        self.sim.cm.map

    # Method to actually move a boat to a given station
    def drive(self, stop):
        old_loc = self.get_location()
        new_loc = stop
        # check if edge to new_loc is existing
        # Todo Implement: Path should exist even though there is no direct edge
        if old_loc.isConnectedTo(new_loc):
            distance = old_loc.get_distance(new_loc)
            bat = self.get_battery()
            # Check if battery sufficient. If yes: move.
            if self.drivable__battery(distance):
                # move
                self.get_location().remove_visitor(self)
                self.discharge(distance)
                self.sim.env.timeout(distance)
                new_loc.add_visitor(self)
                self.set_location(new_loc)
                print("--> Boat %s drove to Station %s. Battery at %s\n" % (
                self.get_id(), self.get_location(), self.get_battery()))
            else:
                print("Cannot drive to any more station. Battery capacity too low.")
        else:
            print("There is no path to this Station")


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
    def charge(self, time):
        if (self.battery + (time * self.charging_speed)) > 100:
            self.battery = 100
            return 100
        else:
            self.battery = self.battery + (time * self.charging_speed)
            return self.battery

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
