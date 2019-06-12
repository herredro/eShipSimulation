import Global as G
import random
import numpy as np

np.random.seed(G.randomseed)
random.seed(G.randomseed)


class Passenger:
    count = 0
    def __init__(self, arrivaltime, dep, dest):
        Passenger.count +=1
        self.id = Passenger.count
        self.time_arrival = arrivaltime
        self.time_boarded = None
        self.time_dispatched = None

        self.dep = dep
        self.dest = dest
        #Todo Simpy: Make passenger Resource
        #self.res = Resource(1)
        self.promised_delay = None
        self.score = {}

    def __str__(self):
        return "P%s:%s->%s"%(self.id, self.dep, self.dest)

    def set_score(self, boat, score):
        self.score[boat] = float(score)

    def finalize(self, distance):
        self.stat_wts = self.time_boarded - self.time_arrival
        self.stat_otb = self.time_dispatched - self.time_boarded - distance


    def get_best_matches(self):
        best_boats = []
        best_score = 10**99
        for boat, score in self.score.items():
            if score < best_score:
                best_score = score
                best_boats = [boat]
            elif score == best_score:
                best_boats.append(boat)
        return best_boats


class Passengers:
    def __init__(self, map, station, stationkeys, seed = None):
        # Todo set seed
        # Todo changed for map-input. Need sim-input?
        self.map = map
        self.station = station.id
        # Todo List of all Stations (int)
        self.passengers = []
        self.stationkeys = stationkeys
        self.arrival_expect = random.randint(1, G.MAX_ARRIVAL_EXPECT)
        #self.map.env.process(self.update_poisson())

    def new(self, arrivaltime=None, dest=None):
        if arrivaltime == None:
            arrivaltime = self.map.env.now
        while dest == None or dest == self.station:
            rand_station = random.randint(0, len(self.stationkeys) - 1)
            dest = self.stationkeys[rand_station]
        new_passenger = Passenger(arrivaltime, self.station, dest)
        self.passengers.append(new_passenger)

    def add_multiple_demand(self, amount=1, arrivaltime=0):
        for i in range (0, amount):
            self.new(arrivaltime=arrivaltime)

    def get_to_dest(self, station):
        station_id = station.id
        list = []
        for passenger in self.passengers:
            if passenger.dest == station_id:
                list.append(passenger)
        return list

    def passengers_boarded(self, to_be_deleted):
        for passenger in to_be_deleted:
            self.passengers.remove(passenger)

    def passenger_boarded(self, to_be_deleted):
        self.passengers.remove(to_be_deleted)


    def update_poisson(self):
        print("SUCCESS POISSON INIT STATION %i" %self.station)
        turn = 1
        while True:
            timestamp = self.map.sim.env.now
            old = len(self.passengers)
            pois = G.poisson_arrivals[self.station-1][turn]
            if self.map.sim.env.now > G.SIMTIME: pois = 0
            self.map.sim.stats.poisson_value_station[self.map.get_station(self.station)][self.map.env.now] = pois
            self.map.sim.stats.poisson_value[self.map.env.now] = pois
            for i in range(pois):
                self.new()
                self.map.sim.stats.accured_demand += 1
            new = len(self.passengers)
            yield self.map.env.timeout(G.INTERARRIVALTIME)
            timepassed = self.map.sim.env.now - timestamp
            for i in range(timepassed):
                self.map.sim.stats.waiting_demand.append(len(self.passengers))
                self.map.sim.stats.waiting_demand_in_time[self.map.sim.env.now] = (len(self.passengers))
            # print("UPDATED DEMAND %s %i-->%i" %(str(self.station), old, new))
            turn += 1
            try:
                self.map.sim.stats.total_demand_in_time[self.map.sim.env.now] += self.map.get_station(self.station).get_demand()

            except KeyError:
                self.map.sim.stats.total_demand_in_time[self.map.sim.env.now] = self.map.get_station(self.station).get_demand()
            try:
                self.map.sim.stats.demand_in_time[self.map.get_station(self.station)][self.map.sim.env.now] += self.map.get_station(self.station).get_demand()
            except KeyError:
                self.map.sim.stats.demand_in_time[self.map.get_station(self.station)][self.map.sim.env.now] = self.map.get_station(self.station).get_demand()