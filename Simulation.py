import NetworkDict
import Boat

class Simulation:

    def __init__(self):
        print("--STARTING SIMULATION--")

        # Controller Map
        self.cm = NetworkDict.Controller_Map()
        self.cm.basic_map()

        # Controller Boats
        self.cb = Boat.Controller_Boat(self.cm.map)
        self.cb.run()

if __name__ == "__main__":
    sim = Simulation()