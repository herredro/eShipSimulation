import Network
import Algorithms.Dijkstra
import Stats
import Global as G
import time


class Strategies:

    def __init__(self, map):
        self.map = map
        self.all_stations = []
        for station in map.get_all_stations():
            self.all_stations.append(station)

    @staticmethod
    def closest_neighbor(map, boat):
        options = boat.get_location().get_connections()
        closest_tuple = sorted(options.items(), key=lambda x: x[1])
        closest_stop = map.get_station(closest_tuple[0][0])
        return closest_stop

    def next_station(self):
        while True:
            i = 1
            while i < len(self.map.get_all_stations())+1:
                next_stop = self.map.get_station(i)
                yield next_stop
                i += 1

    #Todo if occ==cap && next station==curr_stat --> Move somewhere
    @staticmethod
    def highest_demand(map, boat):
        max_station = map.get_station(map.stations.get(0, +1))
        for station in map.get_all_stations():
            if station.get_demand() > max_station.get_demand():
                max_station = station
        return max_station


class Decision_Union:
    def __init__(self, sim):
        self.sim = sim
        self.map = sim.map
        self.boats = self.sim.cb.boats
        self.dijk = Algorithms.Dijkstra.Dijk(self.map)
        self.stats = Stats.Stats_Boat(self.boats)
        # Stations
        self.all_stations = []
        self.pass_dest_at_location = {}
        self.pass_dest_boarded = {}
        # Passengers
        self.passengers_open = []
        self.final_picks = {}
        # Boat
        self.start_restrictions = {}
        self.passenger_restrictions = {}
        self.planned_to_charge_at = {}
        self.charge_now = {}
        self.route_about_to_get_extended = [0, 0]
        self.init_vals()

    def take(self, boat):
        while True:
            # Loop for boat actions
            yield self.sim.env.process(self.dropoff(boat))
            yield self.sim.env.process(self.charge(boat))
            yield self.sim.env.process(self.pickup(boat))
            yield self.sim.env.process(self.drive(boat))

    # Charging Algorithm
    def charge(self, boat):
        start = time.time()
        # if self.boat.idle:
        self.update_vals(boat)
        if self.start_restrictions[boat]:
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
                    if len(doable_distant_chargers) > 3:
                        break
            else: break
        if len(doable_distant_chargers) == 1:
            self.planned_to_charge_at[boat] = doable_distant_chargers[0][1][-1]
            self.start_restrictions[boat] = True
            self.passenger_restrictions[boat] = doable_distant_chargers[0][1]
        if len(doable_distant_chargers) == 0 and type(boat.location) == Network.Charger:
            self.charge_now[boat] = True
        took = (time.time() - start) * 1000
        G.log_comptimes.error("CH:%s:\t%i" % (boat.id, took))
        if self.charge_now[boat]:
            # Decision taken: Going to charge now

            if len(boat.passengers) > 0:
                print("PROBLEM CHARGE: charging with passengers")
            charged = self.sim.env.process(boat.get_location().serve(boat, G.BATTERY))
            self.charge_now[boat] = False
            self.planned_to_charge_at[boat] = None
            self.start_restrictions[boat] = False
            self.passenger_restrictions[boat] = None
            yield charged
        else:
            if len(charger_infos) == 0:
                # No chargers left for boat to avoid 0%
                print("ERROR PLANNING: Big Problem. Will sink.")

    def drive(self, boat):
        next_station = None
        start = time.time()
        if len(boat.route) > G.ROUTE_LENGHT:
            # Route sufficiently long
            next_station = boat.route.pop(0)
            self.route_about_to_get_extended[0]+=1
        else:
            # Route not long enough -> fill
            boat.fill_route_length()
            next_station = boat.route.pop(0)
            self.route_about_to_get_extended[1] += 1
        took = (time.time() - start) * 1000
        G.log_comptimes.error("DR:%s:\t%i" % (boat.id, took))
        boat.stats.luggage[self.sim.env.now] = len(boat.passengers)
        drive = self.sim.env.process(boat.drive(next_station))
        yield drive

    def dropoff(self, boat):
        # Drop-off passengers with destination == boat.location. Method implemented in Boat.py
        dropoff = self.sim.env.process(boat.dropoff())
        yield dropoff

    def pickup(self, boat):
        # Pickup Algorithm:
            #1 get demand at all stations
            #2 sort by priority
            #3 match demands to all boats
        start = time.time()
        self.final_picks[boat] = []

        # Get scores for all passengers at boats location to know which ones boat shall pick (-->final_picks)
        self.passenger_info(boat)
        for passenger in self.passengers_open:
            if passenger.get_best_matches() == []:
                # WARNING: Boat has no best match
                print("ERROR: Passenger has NO best score for boat")
            if passenger.dep == boat.location.id:
                # Just check that passengers location really is boats location
                if boat in passenger.get_best_matches():
                    # Passengers best match is this boat
                    if ((self.start_restrictions[boat] == True and passenger.dest in self.passenger_restrictions)
                            or boat.drivable(passenger.dep, passenger.dest)):
                        # If boat starts having restrictions (due to battery), passenger.dest needs to be still drivable
                        # Also, Passenger.dest needs to be drivable with current battery status
                        new_route = boat.get_route_insert(boat.route, passenger.dest)
                        if new_route[0]:
                            # boat-passenger-scores allow for altered boat-routes. If this is the case, update boats route
                            if G.d_route_change: print("CHANGED ROUTE: %s --> %s" %(boat.route, new_route))
                            boat.route = new_route[1]
                        self.final_picks[boat].append(passenger)
                        passenger.promised_delay = passenger.score[boat]-self.map.get_distance_id(passenger.dep, passenger.dest)
        took = (time.time() - start) * 1000
        G.log_comptimes.error("PU:%s:\t%i" % (boat.id, took))
        # Actual Pickup also, implemented in Boat.py. This method was to define WHAT to pick up
        pickup = self.sim.env.process(boat.pickup_selection(self.final_picks[boat]))
        yield pickup

    # Initialize clean values for decision-making
    def init_vals(self):
        for station in self.map.get_all_stations():
            self.all_stations.append(station)
            self.pass_dest_at_location[station] = []
            for station2 in self.map.get_all_stations():
                self.pass_dest_at_location[station].append([station2])
        for boat in self.boats.values():
            self.final_picks[boat] = []
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

    # Update values for decision-making
    def update_vals(self, boat):
        # Reset values
        for station in self.all_stations:
            for i in range(len(self.pass_dest_at_location[station])):
                self.pass_dest_at_location[station][i][1] = 0
        # Passenger-Destinations at current location
        for station in self.all_stations:
            for station2 in self.all_stations:
                for passenger in boat.location.passengers.passengers:
                    if passenger.dest == station.id:
                        self.pass_dest_at_location[station][station2.id - 1][1] += 1
        # Passenger-Destinations on board
        if len(boat.passengers) > 0:
            for boat in self.boats.values():
                for station in self.all_stations:
                    for passenger in boat.passengers:
                        if passenger.dest == station.id:
                            self.pass_dest_boarded[boat][station.id - 1][1] += 1

    # returns information about reachable possible charging facilities
    def charger_infos(self, boat):
        start = time.time()
        charger_infos = []
        distance = 0
        for i in range(0, len(boat.route) - 1):
            station = self.map.get_station(boat.route[i])
            if i == 0:
                distance += self.sim.map.distances[boat.location][station]
            else:
                distance += self.sim.map.distances[self.map.get_station(boat.route[i - 1])][station]
            if type(station) == Network.Charger:
                charger_infos.append([distance, boat.route[:i + 1]])
        took = (time.time() - start) * 1000
        G.log_comptimes.error("charger_infos():\t%i" % (took))
        return charger_infos

    def passenger_info_ratio(self, boat):
        # update open passengers
        self.passengers_open = []

        for passenger in boat.location.passengers.passengers:
            self.passengers_open.append(passenger)
        # update boat-passenger scores
        start = time.time()
        calculated = 0
        for passenger in self.passengers_open:
            for some_boat in self.boats.values():
                # Calculates pickup_time and drive_time
                pick_up_time = some_boat.wait_time_insert(passenger.dep)
                drive_time   = some_boat.drive_time_insert(passenger.dep, passenger.dest)
                total_time   = pick_up_time[1] + drive_time[1]

                actual_distance = self.sim.map.distances[self.map.get_station(passenger.dep)][self.map.get_station(passenger.dest)]
                pass_waiting_score = float(total_time / actual_distance)
                cap_left = (some_boat.capacity - len(some_boat.passengers))
                operating_grade_score = (1 / cap_left) if (cap_left > 0) else 99

                # Giving penalties for altered routes. Boolean: "altered" in [0]
                penalties = 0
                if pick_up_time[0]:
                    penalties += 1
                if drive_time[0]:
                    penalties += 1
                penalty_discount = G.PENALTY_ROUTE_DIVERSION ** penalties

                passenger.set_score(some_boat, pass_waiting_score * penalty_discount)
                calculated += 1
                # print("sc: %f, py: %f, sc*py: %f" %(pass_waiting_score, penalty_discount, pass_waiting_score*penalty_discount))
            #if boat is not passenger.get_best_matches(): print("present boat not best match")
        # print("calculated %i%%" %(calculated/(len(self.boats)*len(self.passengers_open))*100))
        took = (time.time() - start) * 1000
        G.log_comptimes.error("passenger_scores:\t%i" % (took))

    def passenger_info(self, boat):
        # update open passengers
        self.passengers_open = []

        for passenger in boat.location.passengers.passengers:
            self.passengers_open.append(passenger)
        # update boat-passenger scores
        start = time.time()
        calculated = 0
        for passenger in self.passengers_open:
            for some_boat in self.boats.values():

                wait_time = some_boat.wait_time_insert(passenger.dep)
                drive_time = some_boat.drive_time_insert(passenger.dep, passenger.dest)
                total_time = wait_time[1] + drive_time[1]

                actual_distance = self.sim.map.distances[self.map.get_station(passenger.dep)][
                    self.map.get_station(passenger.dest)]
                pass_waiting_score = float(total_time / actual_distance)
                pass_waiting_score = total_time

                cap_left = (some_boat.capacity - len(some_boat.passengers))
                operating_grade_score = (1 / cap_left) if (cap_left > 0) else 99

                penalties = 0
                if wait_time[0]:
                    penalties += 1
                if drive_time[0]:
                    penalties += 1
                penalty_discount = G.PENALTY_ROUTE_DIVERSION ** penalties

                passenger.set_score(some_boat, pass_waiting_score * penalty_discount)

                calculated += 1
                # print("sc: %f, py: %f, sc*py: %f" %(pass_waiting_score, penalty_discount, pass_waiting_score*penalty_discount))
            # if boat is not passenger.get_best_matches(): print("present boat not best match")
        # print("calculated %i%%" %(calculated/(len(self.boats)*len(self.passengers_open))*100))
        took = (time.time() - start) * 1000
        G.log_comptimes.error("passenger_scores:\t%i" % (took))

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
        strat = self.move_strategy.next_station()
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
            if passenger_restrictions is not None:
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
            next_station = next(strat)
            drive = self.sim.env.process(self.boat.drive(next_station))
            yield drive

    def pickup_priorities(self, restrictions=None):
        self.update_dest_vals()
        prio = []
        if restrictions is not None:
            for i in range(len(restrictions)):
                station = self.map.get_station(restrictions[i])
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
            #distance = self.map.get_distance(self.pass_dest_boarded[station][0], self.boat.location)
            distance = self.sim.map.distances[self.pass_dest_boarded[station][0]][self.boat.location]
            # Don't pick up passengers with dest. boat.loc
            if distance == 0:
                distance = self.dijk.run(self.pass_dest_boarded[station][0].id,
                                         self.boat.location.id)[0][0]
            prio[station][0] = total/distance
        prio_sort = sorted(prio, key=self.sortkey0, reverse=True)
        return prio_sort

    def charge(self, boat):
        self.sim.env.process(boat.location.serve(boat, 100 - boat.battery))

    def update_dest_vals(self):
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