import Network
import Passengers

class Strategies:

    def __init__(self, map):
        self.map = map
        self.all_stations = []
        for station in map.get_all_stations():
            self.all_stations.append(station)

    def run(self):
        print(">>>ERROR<<<>>>STRATEGY_EMPTY<<<")

    @staticmethod
    def closest_neighbor(map, boat):
        options = boat.get_location().get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = map.get_station_object(closest_tuple[0][0])
        return closest_stop

    @staticmethod
    def passenger_prio(map, boat):
        boat.strat.update_vals()


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


    def max_reward(self, map, boat):
        for station in self.all_stations:
            pass




class Decision:
    def __init__(self, sim, boat):
        self.sim = sim
        self.map = sim.map
        self.move_strategy = Strategies(self.map)
        self.boat = boat

        self.all_stations = []
        self.pass_dest_at_location = []
        self.pass_dest_boarded = []

        self.planned_route = []

        for station in self.map.get_all_stations():
            self.all_stations.append(station)
            self.pass_dest_boarded.append([station])
            self.pass_dest_at_location.append([station])
        for i in range (len(self.pass_dest_at_location)):
            self.pass_dest_at_location[i].append(0)
            self.pass_dest_boarded[i].append(0)

    def pickup_priorities(self):
        self.update_vals()
        prio = []
        for station in self.map.get_all_stations():
            prio.append([0])
            prio[station.id-1].append(station)
        for station in range(len(self.all_stations)):
            total = self.pass_dest_at_location[station][1]
            if len(self.boat.passengers) > 0:
                total += self.pass_dest_boarded[station][1]
            distance = self.map.get_distance(self.pass_dest_boarded[station][0], self.boat.location)
            # Don't pick up passengers with dest. boat.loc
            if distance == 0: distance = 99
            prio[station][0] = total/distance
        prio_sort = sorted(prio, key=self.sortkey)
        return prio

    def sortkey(self, item):
        return item[0]

    def update_vals(self):
        # if len(self.boat.passengers) < 1:
        #     return None
        # Reset values
        for i in range (len(self.pass_dest_at_location)):
            self.pass_dest_at_location[i][1] = 0
        # Passenger-Destinations at current location
        for station in self.all_stations:
            for passenger in self.boat.location.passengers.passengers:
                if passenger.dest == station.id:
                    self.pass_dest_at_location[station.id - 1][1] +=1
        # Passenger-Destinations on board
        if len(self.boat.passengers)>0:
            for station in self.all_stations:
                for passenger in self.boat.passengers:
                    if passenger.dest == station.id:
                        self.pass_dest_boarded[station.id-1][1] +=1

    def evaluate(self):
        pass

    def take(self):
        strat = self.move_strategy.closest_neighbor
        #strat = self.move_strategy.max_reward
        while self.map.demand_left():
        #    if self.boat.idle:
            self.update_vals()
            #next_station = self.evaluate()

            at_charger = type(self.boat.location) == Network.Charger
            bat_low = self.boat.battery < 30
            if bat_low & at_charger:
                charged = self.sim.env.process(self.boat.get_location().serve(self.boat, 200))
                yield charged
            next_station = strat(self.map, self.boat)
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

