import Network
import Passengers
import Algorithms.Dijkstra
import Stats
import Global as G


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
        boat.strat.update_dest_vals()


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


class Decision_Union:
    def __init__(self, sim):
        self.sim = sim
        self.map = sim.map
        self.boats = self.sim.cb.boats
        self.dijk = Algorithms.Dijkstra.Dijk(self.map)

        self.all_stations = []
        self.pass_dest_at_location = {}
        self.pass_dest_boarded = {}
        self.final_picks = {}

        self.passengers_open = []
        self.boat_passenger_scores = {}
        self.start_restrictions = {}
        self.passenger_restrictions = {}
        self.planned_to_charge_at = {}
        self.charge_now = {}
        self.init_vals()

    def init_vals(self):

        for station in self.map.get_all_stations():
            self.all_stations.append(station)
            self.pass_dest_at_location[station] = []
            for station2 in self.map.get_all_stations():
                self.pass_dest_at_location[station].append([station2])

        for boat in self.boats.values():
            self.final_picks[boat] = []
            self.boat_passenger_scores[boat] = {}
            self.start_restrictions[boat] = False
            self.passenger_restrictions[boat] = None
            self.planned_to_charge_at[boat] = None
            self.charge_now[boat] = False
            self.pass_dest_boarded[boat] = []
            for station in self.all_stations:
                self.pass_dest_boarded[boat].append([station])

        for station in self.map.get_all_stations():
            for i in range(len(self.pass_dest_at_location[station])):
                self.pass_dest_at_location[station][i].append(0)
            for boat in self.boats.values():
                for i in range(len(self.pass_dest_at_location[station])):
                    self.pass_dest_boarded[boat][i].append(0)

    def update_vals(self, boat):
        # Reset values
        for station in self.all_stations:
            for i in range (len(self.pass_dest_at_location[station])):
                self.pass_dest_at_location[station][i][1] = 0
        # Passenger-Destinations at current location
        for station in self.all_stations:
            for station2 in self.all_stations:
                for passenger in boat.location.passengers.passengers:
                    if passenger.dest == station.id:
                        self.pass_dest_at_location[station][station2.id - 1][1] +=1
        # Passenger-Destinations on board
        if len(boat.passengers)>0:
            for boat in self.boats.values():
                for station in self.all_stations:
                    for passenger in boat.passengers:
                        if passenger.dest == station.id:
                            self.pass_dest_boarded[boat][station.id-1][1] +=1

    def charger_infos(self, boat):
        charger_infos = []
        distance = 0
        for i in range (0, len(boat.route)-1):
            station = self.map.get_station_object(boat.route[i])
            if i==0:
                distance += self.map.get_distance(boat.location, station)
            else:
                distance += self.map.get_distance(self.map.get_station_object(boat.route[i-1]), station)
            if type(station) == Network.Charger:
                charger_infos.append([distance, boat.route[:i+1]])
        return charger_infos

    def passenger_info(self):
        # update open passengers
        self.passengers_open = []
        for station in self.all_stations:
            for passenger in station.passengers.passengers:
                self.passengers_open.append(passenger)
        # update boat-passenger scores
        for boat in self.boats.values():
            for passenger in self.passengers_open:
                self.passenger_to_boat_score_light(passenger, boat)

    def passenger_to_boat_score_light(self, passenger, boat):
        if passenger.dep == boat.location:
            dep_index = -1
        else:
            dep_index = boat.route.index(passenger.dep)
        dest_index = dep_index + boat.route[dep_index:].index(passenger.dest)

        dep_delay = boat.drive_time_index(0, dep_index)
        dest_delay= boat.drive_time_index(dep_index, dest_index)

        actual_distance = self.map.get_distance(self.map.get_station_object(passenger.dep),
                                                self.map.get_station_object(passenger.dest))
        # Todo Check if this gets executed, meaning: there are still passengers with dep=dest...
        self.boat_passenger_scores[boat][passenger] = ((dep_delay + dest_delay) / actual_distance)
        passenger.set_score(boat, ((dep_delay + dest_delay) / actual_distance))
    # except ValueError as e:
    #     #print("P%s:%s->%s not in %s.route:%s: "
    #     # %(passenger.id, passenger.dep, passenger.dest, str(boat), boat.route))
    #     self.boat_passenger_scores[boat][passenger] = 10 ** 99

    def take(self, boat):
        while True:
            #self.sim.map.printmapstate()
            yield self.sim.env.process(self.dropoff(boat))
            #print(">>%s: Yielded dropoff"%str(boat))
            yield self.sim.env.process(self.charge(boat))
            #print(">>%s: Yielded charge"%str(boat))
            yield self.sim.env.process(self.pickup(boat))
            yield self.sim.env.process(self.drive(boat))
            #print(">>%s: Yielded drive"%str(boat))

    def charge(self, boat):
        # if self.boat.idle:
        self.update_vals(boat)
        if self.passenger_restrictions[boat] != None:
            self.passenger_restrictions[boat] = self.passenger_restrictions[boat][1:]
        # POSSIBLE-CHARGERS-EVALUATION
        charger_infos = self.charger_infos(boat)
        pass_dests = boat.get_passenger_destinations()
        # keep if reachable and can drop passengers on the way
        doable_distant_chargers = []
        for charger_info in charger_infos:
            if boat.battery > charger_info[0] * boat.consumption:
                if all(pas_des in charger_info[1] for pas_des in pass_dests):
                    doable_distant_chargers.append(charger_info)
            else: break
        if len(doable_distant_chargers) == 1:
            self.planned_to_charge_at[boat] = doable_distant_chargers[0][1][-1]
        if boat.location.id == self.planned_to_charge_at[boat]:
            self.charge_now[boat] = True
        if self.charge_now[boat]:
            # if start_restrictions:
            if len(boat.passengers) > 0:
                print("PROBLEM CHARGE: charging with passengers")
            charged = self.sim.env.process(boat.get_location().serve(boat, 200))
            self.charge_now[boat] = False
            self.planned_to_charge_at[boat] = None
            self.start_restrictions[boat] = False
            self.passenger_restrictions[boat] = None
            yield charged
        else:
            if len(charger_infos) == 0:
                print("ERROR PLANNING: Big Problem. Will sink.")

    def drive(self, boat):
        if len(boat.route) > 0:
            next_station = boat.route.pop(0)
        else:
            boat.fill_route(simtime=G.SIMTIME*0.1)
            next_station = boat.route.pop(0)
        drive = self.sim.env.process(boat.drive(next_station))
        yield drive

    def dropoff(self, boat):
        dropoff = self.sim.env.process(boat.dropoff())
        yield dropoff

    def pickup(self, boat):
        #1 get demand at all stations
        #2 sort by priority
        #3 match demands to all boats
        self.final_picks[boat] = []
        self.passenger_info()
        for passenger in self.passengers_open:
            if passenger.dep == boat.location.id:
                if passenger.get_best_score() == boat:
                    self.final_picks[boat].append(passenger)
        pickup = self.sim.env.process(boat.pickup_selection(self.final_picks[boat]))
        yield pickup




    def sortkey0(self, item):
        return item[0]



class Decision_Anarchy:
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
            self.update_dest_vals()
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
            cannot_loop = self.boat.battery < (charger_infos[0][0][0] + loop_size) \
                          * self.boat.consumption
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
        self.update_dest_vals()
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
                distance = self.dijk.run(self.pass_dest_boarded[station][0].id,
                                         self.boat.location.id)[0][0]
            prio[station][0] = total/distance
        prio_sort = sorted(prio, key=self.sortkey0, reverse=True)
        return prio_sort




    def evaluate(self):
        pass

    def charge(self, boat):
        self.sim.env.process(boat.location.serve(boat, 100 - boat.battery))

    def update_dest_vals(self):
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