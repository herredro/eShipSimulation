import Controller
import itertools
import random
import simpy
import Simulation

class Simpy:
    def __init__(self, env, sim):
        self.env = env
        self.sim = sim
        self.debug = True
        if self.debug: print("SIMPY START")
        self.action = env.process(self.move_boat())

        #move boat1 to station 3
    def move_boat(self):
        boat1 = self.sim.BoatC.boats[1]
        station3 = self.map.get_station_object(3)
        if self.debug: print("boat starts moving at time %s" % self.env.now)
        duration = boat1.location.get_distance(station3)
        yield self.env.process(self.boats.drive(boat1, station3))
        if self.debug: print("boat arrived at time %s" % self.env.now)

sim = Simulation.Simulation()
control = Controller
control.Maps()
control.Boats()
print(control.Boats.map)

env = simpy.Environment()
boat = Simpy(env, sim)
env.run(until=1000)