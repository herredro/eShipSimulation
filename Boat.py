class Controller_Boat:
    def __init__(self, map):
        print("STARTING BOAT CONTROLLER")
        self.map = map
        self.numBoats = 0
        self.boats = []

    def run(self):
        self.start_basic_boat(2)
        self.boat_moves(0,3)

    def start_basic_boat(self, num):
        numBoats2create = num
        for i in range(1, numBoats2create+1):
            boat = Boat(name=i, map=self.map, location=self.map.get_if_stop(1))
            self.boats.append(boat)
            self.map.get_if_stop(1).add_visitor(boat)
            self.numBoats = self.numBoats + 1

    def boat_moves(self, boat, num):
        for i in range (0,num):
            self.boats[boat].drive_next_closest()


class Boat:
    def __init__(self, name, map, location, battery = 100, charging_speed = 1, consumption = 1):
        self.name = name
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        self.map = map
        self.location = location
        print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.name, self.battery, self.charging_speed, self.consumption))

    def drivable(self, distance):
        if (self.battery - (distance * self.consumption)) > 0: return True
        else: return False

    def drive_next_closest(self):
        print(".BOAT DRIVING ALONE...")
        old_loc = self.location.get_id()
        old_loc_obj = self.location
        new_loc = self.closestStop_tuple()
        new_loc_obj = self.closestStop_object()
        bat = self.battery
        if self.drivable(new_loc[1]):
            self.move(new_loc)
            print("...moved Boat %s from \n\t\torigin=%s to destination=%s\n\t\tDist: %s, Bat: %s-%s"
                  % (str(self),
                     old_loc_obj.get_id(),
                     new_loc_obj.get_id(),
                     new_loc[1],
                     bat, self.battery))
            print(self.map.get_mat())
        else:
            print("Cannot drive to any more station. Battery capacity too low.")

    def move(self, nextStop):
        self.location.remove_visitor(self)
        self.map.get_if_stop(nextStop[0]).add_visitor(self)
        self.location = self.map.get_if_stop(nextStop[0])
        self.battery = self.battery - (nextStop[1] * self.consumption)

    def closestStop_tuple(self):
        options = self.location.get_connections()
        options_sorted = sorted(options.items(), key=lambda x: x[1])

        return options_sorted[0]

    def closestStop_object(self):
        options = self.location.get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_object = self.map.get_if_stop(closest_tuple[0][0])
        return closest_object


    def setLocation(self, loc):
        self.location = loc

    def getLocation(self):
        return self.location

    def getBattery(self):
        return self.battery

    def getBatteryPrint(self):
        print("\t...BATTERY Boat %s: %d%%" %(self.name, self.battery))

    def charge(self, time):
        if (self.battery + (time * self.charging_speed)) > 100:
            self.battery = 100
            return 100
        else:
            self.battery = self.battery + (time * self.charging_speed)
            return self.battery

    def discharge(self, minus):
        self.battery = self.battery - minus

    def getConsumption(self):
        return self.consumption

    def getName(self):
        return self.name

    def getChargingSpeed(self):
        return self.charging_speed

    def toString(self):
        return print("\t...This is Boat %s with \n\t\tbattery=%s, charging_speed=%s, consumption=%s\n" % (
        self.name, self.battery, self.charging_speed, self.consumption))

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)
