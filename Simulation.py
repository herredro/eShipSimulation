import simpy
import Controller as Controller
import Network as Map
import Stats
import Global as G
import Algorithms.Strategies as Strategies
from colorama import Fore, Back, Style
import Boat
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
        data = []
        data.append(self.simpy(True))
        data.append(self.simpy(False))

        self.show_data(data)

    def simpy(self, mode, num_boats = G.NUM_BOATS):
        self.mode = mode
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        print(Style.RESET_ALL)
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)

        if not mode:
            # ANARCHY
            print("BOAT SIMULATOR ANARCHY\nINITIAL SETTINGS:\n")
            self.cb = Controller.Boats(self, mode, num_boats)
        if mode:
            # CENTRAL CONTROL
            print("BOAT SIMULATOR CENTRAL\nINITIAL SETTINGS:\n")
            self.cb = Controller.Boats(self, mode, num_boats)

        self.stats.init()
        for boat in self.cb.boats.values():
            print("B" + str(boat.id) + " Route: ", end="")
            print(boat.route)
        self.cb.start_driving()
        self.map.printmapstate()
        demand_state = []
        for station in self.map.stations.values():
            demand_state.append(station.get_demand())
        self.stats.final_demand = demand_state
        return self.stats

    def show_data(self, runs):
        for run in runs:
            print(run.final_demand)

        colors = ["blue", "red", "green", "blue"]
        col = 0
        for run in runs:
            stations = list(run.demand_in_time.values())
            num = 1
            if run.mode is "Central":
                line = "dashed"
            else:
                line = "dotted"

            for station in stations:
                plt.title('Demand at stations over time with %i boats, IAT:%i, MAE:%i' %(len(self.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
                plt.plot(station.keys(), station.values(), label=run.mode+": S"+str(num), linestyle = line, color=colors[num])
                num += 1
            col += 1
        plt.legend()
        plt.show()
        print(1)



    # def visualization_stations(self):
    #     # STATIONS
    #     # for station in self.map.get_all_stations():
    #     #     self.map.stats.plot_step([self.map.stats.usage_in_time[station]])
    #     print("STATS STATIONS")
    #
    #     for station in self.map.stats.energy_supplied:
    #         print("%s supplied %i units" %(str(station), self.map.stats.energy_supplied[station]))
    #
    #     self.fig, self.ax = plt.subplots()
    #     plt.title("Stations")
    #     for station in self.map.stats.usage_in_time:
    #         self.ax.step(self.map.stats.usage_in_time[station].keys(), self.map.stats.usage_in_time[station].values(), label="Station %s"%str(station))
    #     plt.legend()
    #
    #
    # def visualization_boats(self):
    #     print("Boat passengers")
    #     self.fig2, self.ax2 = plt.subplots()
    #     plt.title("BOATS")
    #     for boat in self.cb.boats.values():
    #         self.ax2.step(boat.stats.luggage.keys(), boat.stats.luggage.values(), label="Boat %s" % str(boat))
    #     plt.legend()


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
