import simpy
import Controller as Controller
import Network as Map
import Passengers
import Global as G
import Algorithms.Strategies as Strategies
from colorama import Fore, Back, Style


class Simulation:
    def __init__(self):
        #SimPy #Todo attach process?
        self.env = simpy.Environment()
        print(Style.RESET_ALL)
        print("BOAT SIMULATOR\nINITIAL SETTINGS:\n")
        self.map = Map.Graph(self.env)
        self.strategy = Strategies.Strategies(self.map)
        # Initial Map can be modified in Global.py
        self.map.create_inital_map()
        self.map.add_initial_demand()
        self.map.generate_initial_demands(G.initial_demand)

        # self.map.get_station_object(1).add_demand(50)
        # self.map.get_station_object(2).add_demand(100)
        # self.map.get_station_object(3).add_demand(150)


        # # Controller Boats #NewBoat: self.cb.new_boat(1, bat=1000)
        self.cb = Controller.Boats(self)

        if G.simpy:             self.simpy()
        elif G.ui_choice:       self.ui_choice()
        elif G.manual:          self.manual()
        else:                   self.strat_pick_drop()

    def ui_choice(self):
        boatnum = input("How many boats? ")
        self.cb.create_basic_boats(numBoats2create=int(boatnum))
        self.cb.printboatlist()
        # Simulation-loop
        choice = input("Choose mode: m=manual, sp=SimPy, s=semi-auto, a=auto (with pickup/dropoff (max): ")
        # Chosen "manual"
        if choice == "m":
            self.cb.move_boat__input()
        # Chosen "pickup_highest_demand"
        elif choice == "sp":
            cont = 1
            while cont:
                self.cb.sp_ui_boat_choice()

            # strategy = self.strategy.highest_demand
            # print("Simpy mode: Pursue highest demand.")
            # rounds = input("How many rounds? ")
            # for i in range(int(rounds)):
            #     self.cb.sp_fleet_move(strategy=strategy)
            # print("stopped at time %s" %self.env.now)
            # self.env.run()
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


    def simpy(self):
        self.cb.create_basic_boats(numBoats2create=2, bat=100)
        strategy = self.strategy.closest_neighbor
        self.cb.sp_fleet_move_algo(strategy)
        #self.env.process(self.cb.sp_fleet_move_algo(strategy))




        # WORKING: UI for fleet coordination with simpy
        #self.cb.sp_ui_fleet_destination()

        # strategy = Strategies.Strategies.closest_neighbor
        # self.cb.sp_fleet_dest_strategy(strategy)
        # self.cb.sp_fleet_dest_strategy(strategy)
        # self.cb.sp_fleet_dest_strategy(strategy)


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
