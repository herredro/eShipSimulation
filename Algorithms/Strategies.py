import Network
import Passengers
import Algorithms.Dijkstra
import Stats

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
        self.boat = boat
        self.move_strategy = Strategies(self.map)
        self.dijk = Algorithms.Dijkstra.Dijk(self.map)


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


    def take(self):
        strat = self.move_strategy.closest_neighbor
        #strat = self.move_strategy.max_reward
        start_restrictions = False
        passenger_restrictions = None
        planned_to_charge_at = None
        charge_now = False
        while True:
            # DROP OFF
            dropoff = self.sim.env.process(self.boat.dropoff())
            yield dropoff
            # if self.boat.idle:
            self.update_vals()
            if passenger_restrictions != None:
                passenger_restrictions = passenger_restrictions[1:]
            loop_size = self.dijk.run(self.boat.location.id, self.boat.location.id)[0][0]
            # POSSIBLE-CHARGERS-EVALUATION
            charger_infos = self.charger_infos()
            # BOOLEANS
            at_charger = type(self.boat.location) == Network.Charger
            bat_low = self.boat.battery < 30
            pass_dests = self.boat.get_passenger_destinations()
            # keep if reachable and can drop passengers on the way
            doable_distant_chargers = []
            for charger_info in charger_infos:
                if self.boat.battery > charger_info[0][0]*self.boat.consumption:
                    if all(pas_des in charger_info[1:] for pas_des in pass_dests):
                        doable_distant_chargers.append(charger_info)
            cannot_loop = self.boat.battery < (charger_infos[0][0][0] + loop_size) * self.boat.consumption
            if self.boat.location.id == planned_to_charge_at:
                charge_now = True
            elif at_charger and len(doable_distant_chargers)==0:
                charge_now = True
            elif (not at_charger) and cannot_loop:
                start_restrictions = True
                planned_to_charge_at = doable_distant_chargers[-1][-1]
                passenger_restrictions = doable_distant_chargers[-1][2:]
            if charge_now:
                #if start_restrictions:
                    if len(self.boat.passengers)>0:
                        print("PROBLEM CHARGE: charging with passengers")
                    charged = self.sim.env.process(self.boat.get_location().serve(self.boat, 200))
                    charge_now = False
                    planned_to_charge_at = None
                    start_restrictions = False
                    passenger_restrictions = None
                    yield charged
            else:
                if len(charger_infos) == 0:
                    print("ERROR PLANNING: Big Problem. Will sink.")


            # PU
            if start_restrictions:
                pickup = self.sim.env.process(self.boat.pickup(restrictions=passenger_restrictions))
            else:
                pickup = self.sim.env.process(self.boat.pickup())
            self.boat.stats.luggage[self.sim.env.now] = len(self.boat.passengers)
            yield pickup
            # REGULAR DRIVE
            self.boat.stats.luggage[self.sim.env.now] = len(self.boat.passengers)
            next_station = strat(self.map, self.boat)
            drive = self.sim.env.process(self.boat.drive(next_station))
            yield drive



    def pickup_priorities(self, restrictions=None):
        self.update_vals()
        prio = []
        if restrictions != None:
            for i in range(len(restrictions)):
                station = self.map.get_station_object(restrictions[i])
                prio.append([0])
                prio[i].append(station)
        else:
            for station in self.map.get_all_stations():
                prio.append([0])
                prio[station.id - 1].append(station)

        for station in range(len(prio)):
            total = self.pass_dest_at_location[station][1]
            if len(self.boat.passengers) > 0:
                total += self.pass_dest_boarded[station][1]
            distance = self.map.get_distance(self.pass_dest_boarded[station][0], self.boat.location)
            # Don't pick up passengers with dest. boat.loc
            if distance == 0:
                distance = self.dijk.run(self.pass_dest_boarded[station][0].id, self.boat.location.id)[0][0]
            prio[station][0] = total/distance
        prio_sort = sorted(prio, key=self.sortkey0, reverse=True)
        return prio_sort




    def evaluate(self):
        pass

    def charge(self, boat):
        self.sim.env.process(boat.location.serve(boat, 100 - boat.battery))

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


    def charger_infos(self):
        charger_infos = []
        for charger in self.map.chargers.values():
            charger_infos.append(self.dijk.run(self.boat.location.get_id(), charger.get_id()))
        # charger_infos = sorted(charger_infos, key=self.sortkey0, reverse=True)
        sortd = sorted(charger_infos, key=self.sortkey0, reverse=False)
        return sortd

    def charger_info_to_dists(self, info):
        charger_dists = []
        for i in range(len(info)):
            charger_dists.append(info[i][0][0])
        return charger_dists


    def sortkey0(self, item):
        return item[0]

    def sortkey000(self, item):
        return item[0][0][0]