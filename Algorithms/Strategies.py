import Network

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

    #Todo if occ==cap && next station==curr_stat --> Move somewhere
    @staticmethod
    def highest_demand(map, boat):
        max_station = map.get_station_object(map.stations.get(0, +1))
        for station in map.get_all_stations():
            if station.get_demand() > max_station.get_demand():
                max_station = station
        return max_station

class Decision:
    def __init__(self, sim, boat):
        self.sim = sim
        self.map = sim.map
        self.move_strategy = Strategies(self.map)
        self.boat = boat

    def take(self):
        while True:
        #    if self.boat.idle:
                # if at charger and bat < 30: charge
                at_charger = type(self.boat.location) == Network.Charger
                bat_low = self.boat.battery < 30
                if bat_low & at_charger:
                    charged = self.sim.env.process(self.boat.get_location().serve(self.boat, 200))
                    yield charged
                next_station = self.move_strategy.closest_neighbor(self.map, self.boat)
                drive = self.sim.env.process(self.boat.drive(next_station))
                yield drive
                # else: next station
                #return next_station

    def takeWORKS(self, boat):
        # if at charger and bat < 30: charge
        at_charger = type(boat.location) == Network.Charger
        bat_low = boat.battery < 30
        if bat_low & at_charger:
            return boat.get_location().serve(boat, 200)
        else:
            next_station = self.move_strategy.closest_neighbor(self.map, boat)
            return boat.drive(next_station)

        # else: next station
        return next_station

    def charge(self, boat):
        self.sim.env.process(boat.location.serve(boat, 100 - boat.battery))

    def pickup(self):
        pass