import Stats
import Global as G
import Algorithms.Strategies as Strat

from colorama import Fore, Back, Style
import logging
import random
import time

random.seed(G.randomseed)


class Boat:
    # Boat specific variables
    count = 0

    def __init__(self, sim, location, battery = 100, capacity = G.CAPACITY, charging_speed = 10, consumption = 1):
        Boat.count+=1
        self.sim = sim
        self.id = (Boat.count)
        self.location = location
        self.capacity = capacity
        self.passengers = []
        # ToDo put this in charger
        self.charging_speed = charging_speed
        self.battery= battery
        self.consumption = consumption
        self.idle = True
        self.stats = Stats.Stats_Boat(self)

        self.strat = Strat.Decision_Anarchy(sim, self)
        self.stats.droveto[0]=location.id
        #Todo Route: Decrease with drive
        self.route = [location.id]
        self.fill_route_length()
        #self.sim.env.process(self.strat.take())

        if G.debug: print("\t...Boat %s created with \n\t\tbattery=%s, charging_speed=%s, consumption=%s" % (self.id, self.battery, self.charging_speed, self.consumption))

    # Todo route: Fill up when empty
    def fill_route_time(self, simtime=G.SIMTIME):
        simtime *= 1.1
        time_needed = 0
        stations = []
        for station in self.sim.map.stations.values():
            stations.append(station.id)
        while time_needed < simtime:
            random_station = random.randint(0, len(stations)-1)
            while stations[random_station] == self.route[-1]:
                random_station = random.randint(0, len(stations) - 1)
            self.route.append(stations[random_station])
            #time_needed += self.sim.map.get_distance(self.sim.map.get_station_object(self.route[-2]), self.sim.map.get_station_object(self.route[-1]))
            time_needed += self.sim.map.distances[self.sim.map.get_station(self.route[-2])][self.sim.map.get_station(self.route[-1])]
        self.route.pop(0)

    def fill_route_length(self):
        stations = []
        for station in self.sim.map.stations.values():
            stations.append(station.id)
        for i in range(G.ROUTE_LENGHT):
            random_station = random.randint(0, len(stations)-1)
            while stations[random_station] == self.route[-1]:
                random_station = random.randint(0, len(stations) - 1)
            self.route.append(stations[random_station])
        self.route.pop(0)

    def drive(self, stop):
        # while True:
            # self.sim.cb.printtime()
            # self.sim.cb.printboatlist()
            # self.sim.map.printmapstate()
            self.idle = 0
            self.old_loc = self.get_location()
            if type(stop) == int:
                self.new_loc = self.sim.map.get_station(stop)
            else: self.new_loc = stop
            #distance = self.sim.map.get_distance(self.old_loc, self.new_loc)
            distance = self.sim.map.distances[self.old_loc][self.new_loc]
            if self.drivable__battery(distance):
                self.sim.stats.boat_load_in_time[self.id][self.sim.env.now] = len(self.passengers)
                self.sim.stats.boat_load[len(self.passengers)] += 1
                self.sim.stats.boat_load_raw.append(len(self.passengers))
                self.sim.stats.boat_load_raw_ratio.append(len(self.passengers)/G.CAPACITY)
                logging.info("SIMPY t=%s: %s started driving to %s" % (self.sim.env.now, str(self), str(stop)))
                print(Fore.BLACK + Back.LIGHTGREEN_EX + "%s:\t%s   \tDRIVING⚡%i%% @%s" % (self.sim.env.now, str(self), self.battery, str(stop)), end='')
                print(Style.RESET_ALL)

                self.old_loc.remove_visitor(self)
                self.set_location(self.new_loc)
                self.discharge(distance)
                yield self.sim.env.timeout(distance+G.DOCK_TIMEOUT)
                self.new_loc.add_visitor(self)
                self.idle = 1

                logging.info("SIMPY t=%s: %s ARRIVED at %s" % (self.sim.env.now, str(self), str(stop)))
                print(Fore.BLACK + Back.GREEN + "%s:\t%s   \tARRIVED\t\t @%s" % (self.sim.env.now, str(self), str(stop)), end='')
                print(Style.RESET_ALL)
                self.stats.droveto[self.sim.env.now] = self.new_loc.id
                self.sim.stats.drovefromto[self.id-1][self.old_loc.id-1][self.new_loc.id] += 1
                self.sim.stats.boat_at_station[self.id-1][self.new_loc.id] += 1
                return distance
            else:
                print("ERROR Battery:\tCannot drive to any more station. Battery capacity too low.")
                return False

    def charge(self, charge_needed):
        #Todo Charge: implement 100 max
        self.idle = 0
        time = int(charge_needed / self.charging_speed)
        yield self.sim.env.timeout(time)
        self.battery = self.battery + charge_needed
        self.idle = 1

    def dropoff(self):
        zim_time = self.sim.env.now
        start = time.time()
        tobedropped = []
        for passenger in self.passengers:
            if passenger.dest == self.location.get_id():
                tobedropped.append(passenger)
        dropped = len(tobedropped)
        for passenger in tobedropped:
            self.passengers.remove(passenger)
            actual_delay = (self.sim.env.now - passenger.arrivaltime) - self.sim.map.get_distance_id(passenger.dep, passenger.dest)
            actual_ratio = (self.sim.env.now - passenger.arrivaltime) / self.sim.map.get_distance_id(passenger.dep,
                                                                                                     passenger.dest)
            # promised waiting times for central control
            if len(passenger.get_best_matches()) > 0:
                promised_ratio = passenger.score[passenger.get_best_matches()[0]]
                self.sim.stats.passenger_promise_deficit.append(passenger.promised_delay - actual_delay)
                passenger.set_dropoff(self.sim.env.now, promised_ratio - actual_ratio)
            self.sim.stats.passenger_processing_delay.append(actual_delay)
            self.sim.stats.dropped_passengers.append(passenger)
            print("delay passenger%s: promised:%s occured:%s" %(str(passenger.id), passenger.promised_delay, actual_delay))

        self.stats.droppedoff[self.sim.env.now] = dropped

        took = (time.time() - start) * 1000
        G.log_comptimes.error("DO:%s:\t%i" % (self.id, took))
        if dropped > 0:
            yield self.sim.env.timeout(G.DROPOFF_TIMEOUT)
            if G.debug_passenger: print(Fore.BLACK + Back.CYAN + "%s:\t%s   \tDROPPED\t%i\t @%s" % (
                self.sim.env.now, str(self), dropped, self.location), end='')
            print(Style.RESET_ALL)
        else:
            yield self.sim.env.timeout(0)

    def pickup(self, amount=None, restrictions=None):
        if self.location.get_demand() > 0:
            #Todo implement restrictions
            before = len(self.passengers)
            space_left = self.capacity - len(self.passengers)
            to_be_pickedup = self.strat.pickup_priorities(restrictions)
            # more, i, new_pas = True, 0, None
            new_pas, i = [], 0
            while len(new_pas) < space_left:
                try:
                    new_pas.extend(self.location.get_demand_to(to_be_pickedup[i][1], space_left-len(new_pas)))
                    i+=1
                except IndexError as e:
                    print("WARNING PICKUP: %s picked up less than could: %s" %(self.id, e))
                    break
            for passenger in new_pas:
                self.passengers.append(passenger)
                self.sim.stats.passenger_waiting_time.append(self.sim.env.now - passenger.arrivaltime)
            after = len(self.passengers)
            self.stats.pickedup[self.sim.env.now] = len(new_pas)
            if len(new_pas) > 0:
                yield self.sim.env.timeout(G.PICK_UP_TIMEOUT)
            else:
                yield self.sim.env.timeout(0)
            # Todo Stats: update reward to Statss-Class
            # Stats.boatreward[self]+=after
            if G.debug_passenger:
                print(Fore.BLACK + Back.LIGHTCYAN_EX + "%s:\t%s   \tPICKED\t%s\t @%s (before:%s)" % (self.sim.env.now, str(self), len(new_pas), str(self.location), before), end='')
                print(Style.RESET_ALL)
        else:
            if G.debug_passenger:
                print(Fore.BLACK + Back.LIGHTCYAN_EX + "%s:\t%s   \tNO DEMAND\t @%s" % (self.sim.env.now, str(self), str(self.location)), end='')
                print(Style.RESET_ALL)

    def pickup_selection(self, list):
        zim_time = self.sim.env.now
        had = len(self.passengers)
        got = 0
        for passenger in list:
            if len(self.passengers) < self.capacity:
                self.passengers.append(passenger)
                passenger.promised_delay = passenger.score[self]
                self.location.passengers.passengers.remove(passenger)
                self.sim.stats.passenger_waiting_time.append(self.sim.env.now - passenger.arrivaltime)
                got +=1
        if got > 0:
            yield self.sim.env.timeout(G.PICK_UP_TIMEOUT)
            if G.debug_passenger:
                print(Fore.BLACK + Back.LIGHTCYAN_EX + "%s:\t%s   \tPICKED\t%s\t @%s (had:%s, now:%s)" % (
                    self.sim.env.now, str(self), got, str(self.location), had, len(self.passengers)), end='')
                print(Style.RESET_ALL)
        else:
            yield self.sim.env.timeout(0)

    # Returns distance in (unchanged) route between two integers
    def drive_time_index(self, frm, to):
        if to == -1:
            focus_route = [self.location].extend(self.route[frm:to+1])
        else:
            focus_route = self.route[frm:to+1]
        if frm == 0:
            #distance = self.sim.map.get_distance(self.location, self.sim.map.get_station_object(focus_route[0]))
            distance = self.sim.map.distances[self.location][self.sim.map.get_station(focus_route[0])]
        else: distance = 0
        for i in range(1,len(focus_route)):
            #distance += self.sim.map.get_distance(self.sim.map.get_station_object(focus_route[i-1]), self.sim.map.get_station_object(focus_route[i]))
            distance += self.sim.map.distances[self.sim.map.get_station(focus_route[i - 1])][self.sim.map.get_station(focus_route[i])]

        return distance

    # returns drive+wait time in (unchanged) route
    def drive_wait_time(self, frm, to):
        return self.drive_time(frm, to) + self.wait_time(frm, to)
    def wait_time(self, frm, to):
        time_wait = 0
        if frm in self.route:
            dep_index = self.route.index(frm)
            if to in self.route[dep_index:]:
                dest_index = dep_index + self.route[dep_index:].index(to)
            else:
                #print("DESTINATION NOT IN ROUTEssjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsj")
                return 10*99
        else:
            #print("DEPARTURE NOT IN ROUTEssjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsj")
            return 10*99
        for i in range(1, dep_index):
            time_wait += self.sim.map.distances[self.sim.map.get_station(self.route[i - 1])][self.sim.map.get_station(self.route[i])]
        return time_wait
    def drive_time(self, frm, to):
        time_driv = 0
        if frm in self.route:
            dep_index = self.route.index(frm)
            if to in self.route[dep_index:]:
                dest_index = dep_index + self.route[dep_index:].index(to)
            else:
                #print("DESTINATION NOT IN ROUTEssjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsj")
                return 10*99
        else:
            #print("DEPARTURE NOT IN ROUTEssjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsjsj")
            return 10*99
        for i in range(dep_index+1, dest_index+1):
            time_driv += self.sim.map.distances[self.sim.map.get_station
            (self.route[i-1])][self.sim.map.get_station(self.route[i])]
        return time_driv

    def wait_time_insert(self, frm):
        route = self.route.copy()
        route.insert(0, self.location.id)
        result = self.get_route_insert(route, frm)
        if result == None:
            return None, 10*99
        if result[0]:
            route = result[1]
            # ToDo route wait time needs inserting location, too?
        index = route.index(frm)
        wait_time = self.time_for_route(route[:index+1])
        return result[0], wait_time

    def drive_time_insert(self, frm, to):
        route = self.route.copy()
        route.insert(0, self.location.id)
        result = self.get_route_insert(route, frm)
        if result == None:
            return None, 10*99
        if result[0]:
            route = result[1]
        index_frm = route.index(frm)

        rest_route = self.get_route_insert(route[index_frm:], to)
        if rest_route == None:
            return None, 10*99

        index_to  = rest_route[1].index(to) + index_frm

        drive_time = self.time_for_route(route[index_frm:index_to+1])
        return rest_route[0], drive_time

    def get_route_insert(self, route, frm):
        for i in range(len(route)):
            if route[i] == frm:
                # frm IN route at position i
                return False, route
            if len(route[i:]) < 2:
                return None
            a = self.sim.map.get_in_between(route[i], route[i+1])
            if a == None:
                break
            if frm in a:
                # frm EN route between position (i, i+1)
                new_route = route.copy()
                new_route.insert(i+1, frm)
                return True, new_route
        # frm not even en route. Not possible.
        return None

    def time_for_route(self, route):
        if type(route) == int or len(route) == 1:
            return 0
        time_drive = 0
        for i in range(len(route) - 1):
            time_drive += self.sim.map.get_distance(self.sim.map.get_station(route[i]),self.sim.map.get_station(route[i + 1]))
        return time_drive

    def drive_stops(self, passenger_loc):
        if passenger_loc in self.route:
            return self.route.index(passenger_loc)
        else:
            return 10*99

    def pickup_any(self, amount):
        if self.location.get_demand() > 0:
            space_left = self.capacity - len(self.passengers)
            for passenger in self.location.get_passengers(space_left):
                self.passengers.append(passenger)
            if amount > space_left:
                if G.debug_passenger: print("%s:\t%s PICKED (only) %s at station %s" % (
                self.sim.env.now, str(self), space_left, str(self.location)))
            else:
                if G.debug_passenger: print(
                    "%s:\t%s PICKED %s at station %s" % (self.sim.env.now, str(self), space_left, str(self.location)))
        else:
            if G.debug_passenger: print(
                "%s:\t%s NO PICKUP cause no demand at %s" % (self.sim.env.now, str(self), str(self.location)))

    def boarded_destinations(self):
        destinations = []
        for station in self.sim.map.get_all_stations():
            destinations.append([station.id, 0])
        for passenger in self.passengers:
            destinations[passenger.dest-1][1] += 1
        return destinations

    def get_passenger_destinations(self):
        boarded_dest = self.boarded_destinations()
        destinations = []
        for tuple in boarded_dest:
            if tuple[1] > 0 and tuple[0] not in destinations:
                destinations.append(tuple[0])
        return destinations

    # Method to check if distance is doable with battery load
    def drivable__battery(self,  distance):
        if (self.get_battery() - (distance * self.get_consumption())) > 0: return True
        else: return False

    def drivable(self, frm, to):
        if self.drivable__battery(self.drive_wait_time(frm, to)):
            return True
        else:
            return False

    def set_location(self, loc):
        self.location = loc

    def get_location(self):
        return self.location

    # Boat knows its battery status
    def get_battery(self):
        return self.battery

    def get_battery__print(self):
        print("\t...BATTERY Boat %s: %d%%" % (self.id, self.battery))

    # Boat looses battery
    def discharge(self, minus):
        self.battery = self.battery - (minus * self.consumption)

    # Boat has a consumption
    def get_consumption(self):
        return self.consumption

    # Boat has an ID
    def get_id(self):
        return self.id

    # Boat has a charging speed
    def get_charging_speed(self):
        return self.charging_speed

    def to_string(self):
        return print("\t...This is Boat %s with \n\t\tbattery=%s, charging_speed=%s, consumption=%s\n" % (
            self.id, self.battery, self.charging_speed, self.consumption))

    def __str__(self):
        if self.idle:
            return "B" + "%s:%s@%s" % (str(self.id), str(len(self.passengers)), self.location)
        else:
            return "B" + "%s:%s@%s" % (str(self.id), str(len(self.passengers)), self.location)

    def __repr__(self):
        return "B" + str(self.id)