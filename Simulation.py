import simpy
import Controller as Controller
import Network as Map

class Simulation:
    def __init__(self):
        self.env = simpy.Environment()
        #Todo Attach process?

        print("BOAT SIMULATOR")
        print("INITIAL SETTINGS:\n")

        self.map = Map.Graph(self.env)
        # Initial Map can be modified in Global.py
        self.map.create_inital_map()
        self.map.get_station_object(1).add_demand(5)
        self.map.get_station_object(2).add_demand(10)
        self.map.get_station_object(3).add_demand(15)

        print("Highest demand at:",self.map.get_highest_demand())


        # Controller Boats
        self.cb = Controller.Boats(self)
        self.cb.new_boat(1, bat=100)
        self.map.printmapstate()
#        drive_proc = self.env.process(self.cb.drive(self.cb.boats[1], self.cm.map.get_station_object(2)))
        self.map.printmapstate()
        #cb.create_basic_boats()
        # manually add boat with: self.cb.new_boat(1, bat=1000)

        # Simulation-loop
        self.cb.move_boat__input()


    def run(self):
        self.env.process(self.boat.drive(5))
        #self.env.process(self.boat.charge(5))
        self.env.process(self.boat.drive(5))

        self.env.run(until=30)

sim = Simulation()
#sim.run()


# env = simpy.Environment()
# bt = simpyy.BoatSP.BoatSP(env)
#
# env.process(bt.drive(5))
# env.run(20)
