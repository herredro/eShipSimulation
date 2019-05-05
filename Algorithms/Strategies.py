test=1
class Strategies:

    def __init__(self, map):
        self.map = map

    def run(self):
        print(">>>ERROR<<<>>>STRATEGY_EMPTY<<<")

    @staticmethod
    def closest_neighbor(map, boat):
        options = boat.get_location().get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = map.get_station_object(closest_tuple[0][0])
        return closest_stop

    @staticmethod
    def highest_demand(map, boat):
        firstkey = map.stations.get(0, +1)
        highest_demand_station = map.stations.get(firstkey)
        for station in map.get_all_stations():
            if station.demand > highest_demand_station.demand:
                highest_demand_station = station
        return highest_demand_station