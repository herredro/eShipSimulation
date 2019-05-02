import Global as G
class Boat:
    # Boat specific variables
    def __init__(self, id, location, battery = 100, charging_speed = 1, consumption = 1, env):
        self.id = ("B" + str(id))
        self.location = location
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))

    def driving(self):

    # # Boat knows its location
    # def set_location(self, loc):
    #     self.location = loc
    #
    # def get_location(self):
    #     return self.location
    #
    # # Boat knows its battery status
    # def get_battery(self):
    #     return self.battery
    #
    # def get_battery__print(self):
    #     print("\t...BATTERY Boat %s: %d%%" % (self.id, self.battery))
    #
    # # Boat initializes its charging procedure
    # def charge(self, time):
    #     if (self.battery + (time * self.charging_speed)) > 100:
    #         self.battery = 100
    #         return 100
    #     else:
    #         self.battery = self.battery + (time * self.charging_speed)
    #         return self.battery
    #
    # # Boat looses battery
    # def discharge(self, minus):
    #     self.battery = self.battery - (minus * self.consumption)
    #
    # # Boat has a consumption
    # def get_consumption(self):
    #     return self.consumption
    #
    # # Boat has an ID
    # def get_id(self):
    #     return self.id
    #
    # # Boat has a charging speed
    # def get_charging_speed(self):
    #     return self.charging_speed
    #
    # def toString(self):
    #     return print("\t...This is Boat %s with \n\t\tbattery=%s, charging_speed=%s, consumption=%s\n" % (
    #         self.id, self.battery, self.charging_speed, self.consumption))
    #
    # def __str__(self):
    #     return str(self.id)
    #
    # def __repr__(self):
    #     return str(self.id)
