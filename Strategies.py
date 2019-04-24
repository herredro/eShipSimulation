class NextStop():

    def __init__(self, map):
        self.map = map

    def closest(self, boat):
        return self.map.get_closest_stop(boat.get_location())