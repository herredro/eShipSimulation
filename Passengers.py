import random
import Network as Map

class Passenger:
    def __init__(self, arrivaltime, dest):
        self.arrivaltime = arrivaltime
        self.dest = dest


class Passengers:
    def __init__(self, map, stationkeys, seed = None):
        #Todo set seed
        #Todo changed for map-input. Need sim-input?
        self.map = map
        #Todo List of all Stations (int)
        self.passengers = []
        self.stationkeys = stationkeys

    def new(self, arrivaltime=None, dest=None):
        if arrivaltime == None:
            arrivaltime = self.map.env.now
        rand_station = random.randint(0, len(self.stationkeys) - 1)
        if dest == None:
            dest = self.stationkeys[rand_station]
        new_passenger = Passenger(arrivaltime, dest)
        self.passengers.append(new_passenger)

    def add_multiple_demand(self, amount=1, arrivaltime=0):
        for i in range (0, amount):
            self.new(arrivaltime=arrivaltime)

    def get_demand_to(self, stationnum):
        demand = []
        for passenger in self.passengers:
            if passenger.dest == stationnum:
                demand.append(passenger)
        #Todo Method to delete occurences in allPassengers (if pas. are taken)
        return demand




# map = Map.Graph()
# # Initial Map can be modified in Global.py
# map.create_inital_map()
#
# passengers = Passengers(map)
# next = passengers.get_new()
# print(next)