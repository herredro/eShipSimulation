import Controller
import Global as G

class Simulation:

    def __init__(self):
        print("BOAT SIMULATOR               ")
        print("INITIAL SETTINGS:\n")

        # Controller Map
        self.cm = Controller.Map()
        self.cm.createBasic4Split()
        #self.cm.map.get_network_tabulate()
        self.cm.printedges_tabulate()

        # Controller Boats
        self.cb = Controller.Boats(self.cm.map)
        self.cb.new_boat(1, bat=1000)
        self.cb.create_basic_boats(4)

        self.cb.printboats_tabulate()
        self.cb.printstate_extended()

        # Run Simulation
        #ToDo not bulletproof.
        self.cb.move__inputboat()

if __name__ == "__main__":
    sim = Simulation()