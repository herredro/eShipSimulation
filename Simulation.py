import Controller
import Global as G
from GUI import Window
from tkinter import *

class Simulation:

    def __init__(self):
        print("BOAT SIMULATOR")
        print("INITIAL SETTINGS:\n")

        # Controller Map
        mapscontroll = Controller.Maps()
        # Initial Map can be modified in Global.py
        mapscontroll.create_inital_map()


        # Controller Boats
        boatscontroll = Controller.Boats(mapscontroll.map)
        boatscontroll.create_basic_boats()
        # manually add boat with: self.cb.new_boat(1, bat=1000)

        #GUI
        # gui = Tk()
        # app = Window(self.gui)
        # gui.mainloop()

        # Simulation-loop
        #ToDo not bulletproof.
        boatscontroll.move_boat__input()
        #boatscontroll.move_station_algorithm(boatscontroll.boats[1], mapscontroll.map.get_station_object(4), "d")

# >>>>>>>>>>>>> RUN THIS <<<<<<<<<<<<<<
if __name__ == "__main__":
    sim = Simulation()