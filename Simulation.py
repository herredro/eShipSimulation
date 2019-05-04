import simpy
import Controller as Controller
import Network as Map
import Global as G
import Algorithms.Strategies as Strategies

class Simulation:
    def __init__(self):
        #SimPy #Todo attach process?
        self.env = simpy.Environment()

        print("BOAT SIMULATOR\nINITIAL SETTINGS:\n")
        self.map = Map.Graph(self.env)
        self.strategy = Strategies.Strategies(self.map)
        # Initial Map can be modified in Global.py
        self.map.create_inital_map()
        self.map.get_station_object(1).add_demand(50)
        self.map.get_station_object(2).add_demand(100)
        self.map.get_station_object(3).add_demand(150)
        # Controller Boats #NewBoat: self.cb.new_boat(1, bat=1000)
        self.cb = Controller.Boats(self)

        if G.ui_choice:         self.ui_choice()
        elif G.manual:          self.manual()
        else:                   self.strat_pick_drop()

    def ui_choice(self):
        boatnum = input("How many boats? ")
        self.cb.create_basic_boats(numBoats2create=int(boatnum))
        self.cb.printboatlist()
        # Simulation-loop
        choice = input("Choose mode: m=manual, s=semi-auto, a=auto (with pickup/dropoff (max): ")
        # Chosen "manual"
        if choice == "m":
            self.cb.move_boat__input()
        # Chosen "pickup_highest_demand"
        elif choice == "s":
            #Todo better UI Output
            while True:
                strategy = input("Pick strategy: h=highest_demand, c=closest_station")
                if strategy == "h":
                    strategy = self.strategy.highest_demand
                    self.cb.fleet_move_demand(strategy=strategy, pu_quant='max', do_quant='max')
                elif strategy == "c":
                    strategy = self.strategy.closest_neighbor
                    self.cb.fleet_move_demand(strategy=strategy, pu_quant='max', do_quant='max')
        elif choice == "a":
            strategy = self.strategy.highest_demand
            print("Automatic mode: Pursue highest demand.")
            rounds = input("How many rounds? ")
            for i in range(int(rounds)):
                self.cb.fleet_move_demand(strategy=strategy, pu_quant='max', do_quant='max')

    def manual(self):
        self.cb.create_basic_boats(numBoats2create=G.numBoats)
        self.cb.move_boat__input()

    def strat_pick_drop(self):
        self.cb.create_basic_boats(numBoats2create=G.numBoats)
        self.cb.printboatlist()
        if G.highestdemand:     strategy = self.strategy.highest_demand
        else:                   strategy = self.strategy.closest_neighbor
        for i in range(int(G.rounds)):
            self.cb.fleet_move_demand(strategy=strategy, pu_quant='max', do_quant='max')

sim = Simulation()
