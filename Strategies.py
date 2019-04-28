class NextStop:

    def __init__(self, map):
        self.map = map

    def closest(self, boat):
        return self.map.closest_neighbor(boat.get_location())

class Algorithms:

    def __init__(self, map):
        self.map = map

    @staticmethod
    def closest_neighbor(map, boat):
        options = boat.get_location().get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = map.get_station_object(closest_tuple[0][0])
        return closest_stop