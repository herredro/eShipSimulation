import NetworkDict
import Boat

class Simulation:

    def __init__(self):
        print("STARTING Simulation")
        print("STARTING Map")
        self.cm = NetworkDict.Controller_Map()
        print("STARTING Boat")
        self.cb = Boat.Controller_Boat(self.cm.map)
        self.basics()

    def basics(self):
        self.cm.basic_map()
        self.cb.run()

if __name__ == "__main__":
    sim = Simulation()





class Controller_Boat:
    def run(self, map):
        self.create_basic_boat()

    def create_basic_boat(self, name):
        numBoats = 3
        for i in (numBoats):
            self.boats.append(Boat.Boat(name=name, map=self.map, location=self.map.get_if_stop(1)))
            self.map.get_if_stop(1).add_visitor(self.boat)


    def boat_moves(self):
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()
        self.boats[0].drive_next_closest()

class Controller_Map:
    def __init__(self):
        print("STARTING MAP CONTROLLER")
        self.map = NetworkDict.Graph()
        self.basic_map()

    def basic_map(self):
        self.map.createBasic3Split()

