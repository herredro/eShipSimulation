import Controller
import Global as G
from GUI import Window
from tkinter import *

class Simulation:

    def __init__(self):
        print("BOAT SIMULATOR")
        print("INITIAL SETTINGS:\n")

        # Controller Map
        self.cm = Controller.Map()
        # Initial Map can be modified in Global.py
        self.cm.create_inital_map()


        # Controller Boats
        self.cb = Controller.Boats(self.cm.map)
        self.cb.create_basic_boats()
        # manually add boat with: self.cb.new_boat(1, bat=1000)

        #self.cb.printboatlist()
        #self.cb.printmapstate()

        #GUI
        # self.gui = Tk()
        # self.app = Window(self.gui)
        # self.gui.mainloop()

        # UI Simulation-loop
        #ToDo not bulletproof.
        self.cb.move_boat__input()

# RUN THIS
if __name__ == "__main__":
    sim = Simulation()