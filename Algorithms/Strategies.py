import Network
import Algorithms.Dijkstra
import Stats
import Global as G
import time
import operator
import random
import numpy as np
random.seed(G.randomseed)


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

    def next_station_rev(self):
        while True:
            i = len(self.map.get_all_stations())
            while i > 0:
                next_stop = self.map.get_station(i)
                yield next_stop
                i -= 1

    #Todo if occ==cap && next station==curr_stat --> Move somewhere
    @staticmethod
    def highest_demand(map, boat):
        max_station = map.get_station(map.stations.get(0, +1))
        for station in map.get_all_stations():
            if station.get_demand() > max_station.get_demand():
                max_station = station
        return max_station

class Decision_Union_New:
    def __init__(self, sim):
        self.sim = sim
        self.map = sim.map
        self.boats = self.sim.cb.boats
        self.dijk = Algorithms.Dijkstra.Dijk(self.map)
        # Stations
        self.all_stations = self.map.get_all_stations()

        # Boat
        self.empty_route = [0,0]
        self.boat_routes = {}
        self.boat_station_scores = {}
        self.same_station = {}
        self.pass_dests = {}
        for boat in self.boats.values():
            self.pass_dests[boat] = []
            self.boat_routes[boat] = []
            self.boat_station_scores[boat] = {}
            self.same_station[boat] = 0
            for station in self.map.get_all_stations():
                self.boat_station_scores[boat][station] = 0


    def take(self, boat):
        while True:
            # Loop for boat actions
            yield self.sim.env.process(self.drive(boat))
            yield self.sim.env.process(self.dropoff(boat))
            yield self.sim.env.process(self.pickup(boat))
            #yield self.sim.env.process(self.charge(boat))

    def score1(self, demand_pickable, expectation, distance):
        score = (demand_pickable + ((expectation/G.INTERARRIVALTIME)*distance))/distance
        return score

    def score2(self, demand_pickable, expectation, distance):
        score = (demand_pickable + ((expectation/G.INTERARRIVALTIME)*distance))/distance**1/(demand_pickable+1)
        return score

    def drive(self, boat):
        # calc route
        if len(boat.passengers) > 0:

            self.empty_route[0] += 1
            boarded_dest = boat.boarded_destinations_dict()
            route = self.calc_route_d({boat.location: len(boat.passengers)}, boarded_dest)
            self.boat_routes[boat] = route[1][1:]
            next_station = self.boat_routes[boat].pop(0)
        else:
            self.boat_routes[boat] = []
            self.empty_route[1] += 1
            for station in self.all_stations:
                demand = len(station.passengers.passengers)
                cap_left = boat.capacity - len(boat.passengers)
                demand_pickable = demand if demand <= cap_left else cap_left
                expectation = station.passengers.arrival_expect
                distance = self.map.get_distance(boat.location, station)
                distance = distance if distance > 0 else 1
                score = self.score1(demand_pickable, expectation, distance)
                self.boat_station_scores[boat][station] = score
            keys = list(self.boat_station_scores[boat].keys())
            values = list(self.boat_station_scores[boat].values())
            max_key = values.index(max(values))
            max_station = keys[max_key]
            next_station = max_station
        # #ToDO Central: Calc these ratios for all boats, then compare
        # No existing route --> drive to best station
        if next_station == boat.location:
            score_this = self.boat_station_scores[boat][next_station]
            # If other boats score for this station is at least half of this one's:
            # choose new next_station
            score_other = self.get_boat_scores_for_station(next_station)
            other_option = False
            for other_boat in self.get_boat_scores_for_station(next_station):
                # ToDo Could be better
                if other_boat == boat:
                    continue
                if score_other[other_boat] > score_this/2:
                    other_option = True
            if other_option and len(self.boat_routes[boat]) < 1:
                keys.remove(next_station)
                values.remove(score_this)
                max_key = values.index(max(values))
                max_station = keys[max_key]
                next_station = max_station
                drive = self.sim.env.process(boat.drive(next_station))
                yield drive
            elif self.same_station[boat] < 1:
                # Todo implement a wait function?
                if G.live: print("Boat %s decided to stay and wait" %str(boat.id))
                self.same_station[boat] += 1
                yield self.sim.env.timeout(10)
            else:
                drive = self.sim.env.process(boat.drive(next_station))
                yield drive
        else:
            drive = self.sim.env.process(boat.drive(next_station))
            yield drive

    def get_boat_scores_for_station(self, station):
        scores = {}
        for boat in self.boats.values():
            scores[boat] = self.boat_station_scores[boat][station]
        return scores

    def UPD_of_list(self, passenger_list):
        mix = []
        for passenger in passenger_list:
            if passenger.dest not in mix:
                mix.append(passenger.dest)
        return mix


    # Boat empty -> PU most frequent destination --> recall pickup()
    def pickup_empty(self, boat, passengers):
        picks = []
        request_destinations = {}
        for passenger in passengers:
            # Calculating destination frequencies of demand at boats current location
            try:
                request_destinations[self.map.get_station(passenger.dest)] += 1
            except KeyError:
                request_destinations[self.map.get_station(passenger.dest)] = 1

        # Todo This can be done with all boats and then decide
        if request_destinations != {}:
            most_prominent_destination = max(request_destinations.items(), key=operator.itemgetter(1))[0]
            pickable = list(boat.location.passengers.get_to_dest(most_prominent_destination))
            while len(pickable) > 0:
                picks.append(pickable.pop(0))
                passengers.remove(picks[-1])
                request_destinations[most_prominent_destination] -= 1
                # TODO: WEAK
                if len(boat.passengers) >= boat.capacity:
                    break
            if len(pickable) == 0:
                del (request_destinations[most_prominent_destination])
            if len(boat.passengers) >= boat.capacity:
                pass
        return passengers, picks

    def pickup_non_empty(self, boat, passengers, picks):
    # Boat non-empty -> UPD-conform -> UPD-extension
        cap_left = boat.capacity - len(boat.passengers) - len(picks)
        alpha_cap = False
        if cap_left < 1 or (len(self.UPD_of_list(boat.passengers + picks)) >= G.ALPHA_DESTINATION_MIX):
            alpha_cap = True
        request_destinations = {}
        for passenger in passengers:
            try:
                request_destinations[self.map.get_station(passenger.dest)] += 1
            except KeyError:
                request_destinations[self.map.get_station(passenger.dest)] = 1

        # Only proceed if passengers left at station AND still alpha-conform and seats left
        if len(request_destinations)>= 1:
            upd_conform = []
            upd = self.UPD_of_list(boat.passengers + picks)
            #[upd_conform.append(station) if station in upd else None for station in request_destinations.keys()]
            for station in request_destinations.keys():
                if station.id in upd:
                    upd_conform.append(station)
            most_prominent_destination = max(request_destinations.items(), key=operator.itemgetter(1))[0]
            while most_prominent_destination not in upd_conform:
                try:
                    del (request_destinations[most_prominent_destination])
                    most_prominent_destination = max(request_destinations.items(), key=operator.itemgetter(1))[0]
                except ValueError:
                    if alpha_cap:
                        return [], picks
                    break
            pickable = []
            [pickable.append(pas) if pas.dest == most_prominent_destination.id else None for pas in passengers]
            while len(pickable) > 0 and cap_left > 0:
                picks.append(pickable.pop(0))
                passengers.remove(picks[-1])
                cap_left -= 1
            return passengers, picks

    def pickup(self, boat):
        passengers = boat.location.passengers.passengers.copy()
        cap_left = boat.capacity - len(boat.passengers)
        picks = []
        if len(boat.passengers) + len(picks) < 1:
            # Scenario: Boat empty
            passengers, picks = self.pickup_empty(boat, passengers)
        while len(picks) < cap_left and len(passengers) > 0 and (len(self.UPD_of_list(boat.passengers + picks)) <= G.ALPHA_DESTINATION_MIX):
            # Scenario: Boat non-empty (loop)
            passengers, picks = self.pickup_non_empty(boat, passengers, picks)
        pickup = self.sim.env.process(boat.pickup_selection(picks))
        yield pickup

        # calc route
        # if len(boat.passengers) > 0:
        #     # OLD route_calc with list:
        #     # boarded_dest = boat.boarded_destinations_light()
        #     # to_route = [self.map.get_station(station_id) for station_id in boarded_dest]
        #     boarded_dest = boat.boarded_destinations_dict()
        #     route = self.calc_route_d({boat.location: len(boat.passengers)}, boarded_dest)
        #     self.boat_routes[boat] = route[1][1:]
        # else:
        #     self.boat_routes[boat] = []

    def calc_route_d(self, ffs, to_route):
        if len(to_route) == 1:
            #new_ffs = (next(iter(ffs)), next(iter(ffs.values())))
            new_ffs = list(ffs.items())[0]
            to = list(to_route.items())[0]
            distance = self.map.get_distance(new_ffs[0], to[0])
            discount = 1 + G.BETA_DISCOUNT_RECURSION * 0.5 * (1-(new_ffs[1] / G.CAPACITY))
            ret_val = [distance * (discount), [new_ffs[0], to[0]]]
            return ret_val
        else:
            ffs2first = []
            subprblm = []
            for station in to_route:
                station_freq = to_route[station]
                ffs2first.append(self.calc_route_d(ffs, {station:to_route[station]}))
                less = to_route.copy()
                del less[station]
                subprblm.append(self.calc_route_d({station:station_freq}, less))
            final_scores = [a[0] + b[0] for a, b in zip(ffs2first, subprblm)]
            ind = int(np.argmin(final_scores))
            merged_score = ffs2first[ind][0] + subprblm[ind][0]
            merged_path = list(ffs2first[ind][1])
            merged_path.extend(subprblm[ind][1][1:])
            ret_val = [merged_score, merged_path]
            return ret_val


    def calc_route(self, begin, to_route):
        if len(to_route) == 1:
            distance = self.map.get_distance(begin, to_route[0])
            ret_val = [distance, [begin, to_route[0]]]
            return ret_val
        else:
            sub1s = []
            sub2s = []
            for station in to_route:
                sub1s.append(self.calc_route(begin, [station]))
                less = to_route.copy()
                less.remove(station)
                sub2s.append(self.calc_route(station, less))
            final_scores = [a[0] + b[0] for a, b in zip(sub1s, sub2s)]
            ind = int(np.argmin(final_scores))
            merged_score = sub1s[ind][0] + sub2s[ind][0]
            merged_path = list(sub1s[ind][1])
            merged_path.extend(sub2s[ind][1][1:])
            ret_val = [merged_score, merged_path]
            return ret_val



    def dropoff(self, boat):
        # Drop-off passengers with destination == boat.location. Method implemented in Boat.py
        dropoff = self.sim.env.process(boat.dropoff())
        yield dropoff

    def sortkey0(self, item):
        return item[0]


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
            yield self.sim.env.process(self.drive(boat))
            yield self.sim.env.process(self.dropoff(boat))
            yield self.sim.env.process(self.pickup(boat))
            #yield self.sim.env.process(self.charge(boat))

    def fill_route_length(self, boat):
        for i in range(len(self.boats)):
            stations = []
            for station in self.sim.map.stations.values():
                stations.append(station.id)
            for i in range(G.ROUTE_LENGHT):
                random_station = random.randint(0, len(stations)-1)
                while stations[random_station] == boat.route[-1]:
                    random_station = random.randint(0, len(stations) - 1)
                boat.route.append(stations[random_station])
            boat.route.pop(0)

    def drive(self, boat):
        # best_next = self.station_scores(boat)
        # best_next = self.map.get_station(best_next)
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
        #next_station = best_next
        if next_station == boat.location:
            print("NIET GOED: NEXT LOC IS BOAT.LOC")
        drive = self.sim.env.process(boat.drive(next_station))
        yield drive

    def pickup(self, boat):
        # Pickup Algorithm:
            #1 get demand at all stations
            #2 sort by priority
            #3 match demands to all boats
        start = time.time()
        zim_time=self.sim.env.now
        self.final_picks[boat] = []
        # Get scores for all passengers at boats location to know which ones boat shall pick (-->final_picks)
        self.passenger_info(boat)
        a = False
        remaining_capactiy = boat.capacity - len(boat.passengers)
        for passenger in self.passengers_open:
            if (len(self.final_picks[boat]) < remaining_capactiy):
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
                            if new_route == None:
                                break
                            elif new_route[0]:
                                # boat-passenger-scores allow for altered boat-routes. If this is the case, update boats route
                                if G.d_route_change: print("CHANGED ROUTE: %s --> %s" %(boat.route, new_route))
                                boat.route = new_route[1]

                            self.final_picks[boat].append(passenger)

                            if passenger.id == G.d_p_num: a = True
        took = (time.time() - start) * 1000
        G.log_comptimes.error("PU:%s:\t%i" % (boat.id, took))
        # Actual Pickup also, implemented in Boat.py. This method was to define WHAT to pick up

        pickup = self.sim.env.process(boat.pickup_selection(self.final_picks[boat]))
        yield pickup

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



    # def check_best_next_station(self, boat):
    #     scores = dict.fromkeys(self.all_stations, 0)
    #     for station in self.all_stations:
    #         if station == boat.location:
    #             del(scores[station])
    #             continue
    #         travel_time = self.map.get_distance(boat.location, station)
    #         demand = len(station.passengers.passengers)
    #         scores[station] = demand/travel_time
    #     return scores

    def dropoff(self, boat):
        # Drop-off passengers with destination == boat.location. Method implemented in Boat.py
        dropoff = self.sim.env.process(boat.dropoff())
        yield dropoff

    def station_scores(self, boat):
        # update open passengers
        station_sc = []
        # update boat-passenger scores
        start = time.time()
        calculated = 0
        for station in self.all_stations:
            station_sc.append(0)
            for passenger in station.passengers.passengers:
                wait_time_now = boat.wait_time(passenger.dep, passenger.dest)
                wait_time = wait_time_now + (self.sim.env.now - passenger.arrivaltime)
                drive_time = boat.drive_time(passenger.dep, passenger.dest)
                total_time = wait_time + drive_time

                actual_distance = self.sim.map.distances[self.map.get_station(passenger.dep)][
                    self.map.get_station(passenger.dest)]
                score = float(total_time - actual_distance)

                cap_left = (boat.capacity - len(boat.passengers))
                operating_grade_score = (1 / cap_left) if (cap_left > 0) else 99
                passenger.set_score(boat, score)
                station_sc[self.all_stations.index(station)] += score
        best_station = station_sc.index(max(station_sc))+1
        return best_station


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

    def passenger_info(self, boat, location=None):
        if location == None:
            location = boat.location
        # update open passengers
        self.passengers_open = []
        for passenger in location.passengers.passengers:
            self.passengers_open.append(passenger)
        # update boat-passenger scores
        start = time.time()
        calculated = 0
        for passenger in self.passengers_open:
            for some_boat in self.boats.values():
                wait_time_now = some_boat.wait_time_insert(passenger.dep)
                wait_time = [wait_time_now[0], wait_time_now[1] + (self.sim.env.now - passenger.arrivaltime)]
                drive_time = some_boat.drive_time_insert(passenger.dep, passenger.dest)
                total_time = wait_time[1] + drive_time[1]
                actual_distance = self.sim.map.distances[self.map.get_station(passenger.dep)][
                    self.map.get_station(passenger.dest)]
                pass_waiting_score = float(total_time - actual_distance)


                cap_left = (some_boat.capacity - len(some_boat.passengers))
                operating_grade_score = (1 / cap_left) if (cap_left > 0) else 99

                penalties = 0
                if wait_time[0]:
                    penalties += 1
                if drive_time[0]:
                    penalties += 1
                penalty_discount = G.PENALTY_ROUTE_DIVERSION ** penalties
                score = pass_waiting_score * penalty_discount

                passenger.set_score(some_boat, score)
                calculated += 1
        print("calculated %i%%" %(calculated/(len(self.boats)*len(self.passengers_open))*100))
        took = (time.time() - start) * 1000
        G.log_comptimes.error("passenger_scores:\t%i" % (took))

    def passenger_infoCOMPLETE(self):
        # update open passengers
        self.passengers_open = []
        for station in self.all_stations:
            for passenger in station.passengers.passengers:
                self.passengers_open.append(passenger)
        # update boat-passenger scores
        start = time.time()
        calculated = 0
        for boat in self.boats.values():
            for passenger in self.passengers_open:
                if boat.drive_stops(passenger.dep) < 1:
                    drive_time = boat.drive_time(passenger.dep, passenger.dest)
                    actual_distance = self.sim.map.distances[self.map.get_station(passenger.dep)][
                        self.map.get_station(passenger.dest)]
                    self.boat_passenger_scores[boat][passenger] = (drive_time / actual_distance)
                    passenger.set_score(boat, (drive_time / actual_distance))
                    calculated += 1
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
        if boat.id % 2 == 0:
            self.strat = self.move_strategy.next_station_rev()
        else:
            self.strat = self.move_strategy.next_station()

        for station in self.map.get_all_stations():
            self.all_stations.append(station)
            self.pass_dest_boarded.append([station])
            self.pass_dest_at_location.append([station])
        for i in range (len(self.pass_dest_at_location)):
            self.pass_dest_at_location[i].append(0)
            self.pass_dest_boarded[i].append(0)

    def take(self):
        start_restrictions = False
        passenger_restrictions = None
        planned_to_charge_at = None
        charge_now = False
        while True:
            # DROP OFF
            dropoff = self.sim.env.process(self.boat.dropoff())
            yield dropoff
            self.update_dest_vals()
            if passenger_restrictions is not None:
                passenger_restrictions = passenger_restrictions[1:]
            # PU
            pickup = self.sim.env.process(self.boat.pickup_fifo())
            yield pickup
            # REGULAR DRIVE
            next_station = next(self.strat)
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
                if distance == 0: distance = 1
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