import simpy

class Simulation:
    def __init__(self):
        env = simpy.Environment()

        env.run()

sim = Simulation()
sim.run