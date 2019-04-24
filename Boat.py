import Global as G
class Boat:
    def __init__(self, id, location, battery = 100, charging_speed = 1, consumption = 1):
        self.id = ("B" + str(id))
        self.location = location
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))


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
