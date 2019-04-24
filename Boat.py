import NetworkDict

class Controller_Boat:
    def __init__(self, map):
        print("--STARTING BOAT CONTROLLER--")
        self.map = map
        self.numBoats = 0
        self.boats = []

    def run(self):
        self.create_basic_boats(2)
        self.map.print_mat()
        self.move_multiple__closest(self.boats[0], 7)

    def create_basic_boats(self, num):
        numBoats2create = num
        for i in range(0, numBoats2create):
            boat = Boat(id=i, location=self.map.get_if_stop(1))
            self.boats.append(boat)
            self.map.get_if_stop(1).add_visitor(boat)
            self.numBoats = self.numBoats + 1

    def move_multiple__closest(self, boat, num):
        for i in range (0,num):
            to = self.map.get_closest_stop(boat.get_location())
            self.drive(self.boats[boat.get_id()], to)

    def drivable__battery(self, boat, distance):
        if (boat.get_battery() - (distance * boat.get_consumption())) > 0: return True
        else: return False

    def drive(self, boat, stop):
        print(".BOAT DRIVING ALONE...")
        old_loc = boat.get_location()
        new_loc = stop
        distance = old_loc.get_distance(new_loc)
        bat = boat.get_battery()
        if self.drivable__battery(boat, distance):
            #move
            boat.get_location().remove_visitor(boat)
            #self.map.get_if_stop(stop).add_visitor(boat)
            new_loc.add_visitor(boat)
            boat.set_location(new_loc)
            boat.discharge(distance)

            print("...moved Boat %s from \n\t\torigin=%s to destination=%s\n\t\tDist: %s, Bat: %s-%s"
                  % (str(boat),
                     old_loc.get_id(),
                     new_loc.get_id(),
                     distance,
                     bat, boat.get_battery()))
            print(self.map.get_mat())
        else:
            print("Cannot drive to any more station. Battery capacity too low.")



class Boat:
    def __init__(self, id, location, battery = 100, charging_speed = 1, consumption = 1):
        self.id = id
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        #self.map = map
        self.location = location
        print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))


    def set_location(self, loc):
        self.location = loc

    def get_location(self):
        return self.location

    def get_battery(self):
        return self.battery

    def get_battery__print(self):
        print("\t...BATTERY Boat %s: %d%%" % (self.id, self.battery))

    def charge(self, time):
        if (self.battery + (time * self.charging_speed)) > 100:
            self.battery = 100
            return 100
        else:
            self.battery = self.battery + (time * self.charging_speed)
            return self.battery

    def discharge(self, minus):
        self.battery = self.battery - (minus * self.consumption)

    def get_consumption(self):
        return self.consumption

    def get_id(self):
        return self.id

    def get_charging_speed(self):
        return self.charging_speed

    def toString(self):
        return print("\t...This is Boat %s with \n\t\tbattery=%s, charging_speed=%s, consumption=%s\n" % (
            self.id, self.battery, self.charging_speed, self.consumption))

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)
