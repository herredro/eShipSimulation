import simpy
import Controller as Controller
import Network as Map
import Passengers
import Global as G
import Algorithms.Strategies as Strategies
from colorama import Fore, Back, Style
import Stats
import matplotlib.pyplot as plt



class Simulation:
    def __init__(self):
        #SimPy #Todo attach process?

        # if G.simpy:             self.simpy()
        # elif G.ui_choice:       self.ui_choice()
        # elif G.manual:          self.manual()
        # else:                   self.strat_pick_drop()

        # for i in range(100):
        #     self.simpy(i)
        self.simpy(2)
        plt.show()

    def simpy(self, numboats):
        self.env = simpy.Environment()
        print(Style.RESET_ALL)
        print("BOAT SIMULATOR\nINITIAL SETTINGS:\n")
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)
        self.cb = Controller.Boats(self)

        self.cb.new_boat(1, loc=self.map.get_station_object(1), bat=100, cons=0.5)
        self.cb.new_boat(2, loc=self.map.get_station_object(2), bat=100, cons=1)
        self.cb.new_boat(3, loc=self.map.get_station_object(3), bat=100, cons=2)
        # self.cb.create_basic_boats(numBoats2create=numboats, bat=100)

        self.map.printmapstate()

        self.env.run(until=1000)
        self.cb.printboatlist()
        self.map.printmapstate()

        self.visualization_stations()

        self.visualization_boats()


        # boat = self.cb.boats[1]
        # plot = boat.stats.plot_free([boat.stats.pickedup, boat.stats.droppedoff])
        # plot.show()


        # boat.stats.save_dict(boat.stats.droveto)
        # boat.stats.open_dict("data.txt")

    def visualization_stations(self):
        # STATIONS
        # for station in self.map.get_all_stations():
        #     self.map.stats.plot_step([self.map.stats.usage_in_time[station]])
        print("STATS STATIONS")

        for station in self.map.stats.energy_supplied:
            print("%s supplied %i units" %(str(station), self.map.stats.energy_supplied[station]))

        self.fig, self.ax = plt.subplots()
        plt.title("Stations")
        for station in self.map.stats.usage_in_time:
            self.ax.step(self.map.stats.usage_in_time[station].keys(), self.map.stats.usage_in_time[station].values(), label="Station %s"%str(station))
        plt.legend()


    def visualization_boats(self):
        print("Boat passengers")
        self.fig2, self.ax2 = plt.subplots()
        plt.title("BOATS")
        for boat in self.cb.boats.values():
            self.ax2.step(boat.stats.luggage.keys(), boat.stats.luggage.values(), label="Boat %s" % str(boat))
        plt.legend()


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

sim = Simulation()
