import random
import Network as Map
random.seed(123)
from simpy import Resource
import numpy as np
np.random.seed(123)
import Global as G

class Passenger:
    count = 0
    def __init__(self, arrivaltime, dep, dest):
        Passenger.count +=1
        self.id = Passenger.count
        self.arrivaltime = arrivaltime
        # Todo metrics record waiting time
        self.time_processed = -10000
        self.dep = dep
        self.dest = dest
        #Todo Simpy: Make passenger Resource
        #self.res = Resource(1)


    def __str__(self):
        return "P%s:%s->%s"%(self.id, self.dep, self.dest)


class Passengers:
    def __init__(self, map, station, stationkeys, seed = None):
        #Todo set seed
        #Todo changed for map-input. Need sim-input?
        self.map = map
        self.station = station.id
        #Todo List of all Stations (int)
        self.passengers = []
        self.stationkeys = stationkeys
        self.arrival_expect = random.randint(0, G.MAX_ARRIVAL_EXPECT)
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

    def update_poisson(self):
        while True:
            old = len(self.passengers)
            pois = np.random.poisson(self.arrival_expect)
            for i in range(pois):
                self.new()
            new = len(self.passengers)
            yield self.map.env.timeout(G.INTERARRIVALTIME)
            print("UPDATED DEMAND %s %i-->%i" %(str(self.station), old, new))




# map = Map.Graph()
# # Initial Map can be modified in Global.py
# map.create_inital_map()
#
# passengers = Passengers(map)
# next = passengers.get_new()
# print(next)