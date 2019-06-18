import simpy
import Controller as Controller
import Network as Map
import Stats
import Global as G
from Parameters import Parameters
from Passengers import Passenger
import Algorithms.Strategies as Strategies
from colorama import Fore, Back, Style
import random
import csv
import numpy as np


class Simulation:
    def __init__(self):
        capacity = 30
        self.EXPERIMENT_NAME = "Centralcap30"

        hoho, central = [], []

        # num_boats, capacity = self.csv_in('csv/numb-cap.csv')
        alpha, beta = self.csv_in("csv/in/ab.csv")
        self.csv_out_init(self.EXPERIMENT_NAME)

        num_boats = [i*5 for i in range(1,21)]
        num_boats.insert(0,1)
        #num_boats = np.linspace(1,150,50, dtype=int)



        RUNS = len(num_boats)
        #ran = [random.randint(1,100) for i in range(RUNS)]



        for i in range(RUNS):

            hoho.append(self.combined(True, num_boats=num_boats[i], capacity=capacity))





            # hoho.append(self.combined(True,
            #                             #random_seed=ran[i],
            #                             num_boats=40,
            #                             capacity=10,
            #                             alpha=alpha[i],
            #                             beta=beta[i]
            #                           ))
            print(i/RUNS)

        self.stats.macro__summary(hoho)
        #self.stats.macro__plot_num_cap(hoho)

        # data.append(self.simpy(False))
        random.seed(G.randomseed)
        # data.append(self.simpy(True))

        #self.stats.print_data(central)
        if G.visuals: self.stats.macro__plot_data(central)

    def csv_in(self, file):
        first, second = [], []
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                first.append(int(eval(row['first'])))
                second.append(int(eval(row['second'])))
        return first, second

    def csv_out_init(self, name):
        with open('csv/out/%s.csv'%name, mode='w') as csv_file:
            fieldnames = [
            'simtime',
            'num_stations',
            'num_boats',
            'capacity',
            'alpha',
            'beta',
            'randomseed',
            'mn_boatload_ratio',
            'p_wts',
            'p_otb',
            'mn_waiting_demand',
            'dem_occ',
            'dem_left',
            'satisfied']
            csv_file.write("sep=,\n")
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    def csv_out(self, stats, name):
        with open('csv/out/%s.csv'%self.EXPERIMENT_NAME, mode='a') as csv_file:
            fieldnames = [
            'simtime',
            'num_stations',
            'num_boats',
            'capacity',
            'alpha',
            'beta',
            'randomseed',
            'mn_boatload_ratio',
            'p_wts',
            'p_otb',
            'mn_waiting_demand',
            'dem_occ',
            'dem_left',
            'satisfied']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(stats)

    def combined(self, central, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, expected_arrivals=G.expected_arrivals, random_seed=G.randomseed):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, expected_arrivals, random_seed)
        print("--CENTRAL--") if central else print("--HOHO--")
        self.params.print()
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)
        self.cb = Controller.Boats(self, self.central)
        self.stats.init()
        self.cb.start_now()
        self.stats.final_demand = [station.get_demand() for station in self.map.stations.values()]
        Passenger.count = 0
        self.stats.micro__analyze_data()
        self.stats.micro__print_data_light()
        self.csv_out(self.stats.csv_output(), self.EXPERIMENT_NAME)
        return self.stats

    def hoho(self, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, init_demand=G.initial_demand):
        self.central = False
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, init_demand)
        print("--HOHO--")
        self.params.print()
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        #print(Style.RESET_ALL)
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)
        self.cb = Controller.Boats(self, self.central)
        self.stats.init()
        self.cb.start_now()
        self.stats.final_demand = [station.get_demand() for station in self.map.stations.values()]
        Passenger.count = 0
        self.stats.micro__analyze_data()
        self.stats.micro__print_data_light()
        return self.stats

    def central(self, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, init_demand=G.initial_demand):
        self.central = True
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, init_demand)
        print("--CENTRAL--")
        self.params.print()
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        #print(Style.RESET_ALL)
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)
        self.cb = Controller.Boats(self, self.central)
        self.stats.init()
        self.cb.start_now()
        self.stats.final_demand = [station.get_demand() for station in self.map.stations.values()]
        Passenger.count = 0
        self.stats.micro__analyze_data()
        self.stats.micro__print_data_light()
        return self.stats

    def simpy(self, mode, num_boats = G.NUM_BOATS):
        self.central = mode
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        #print(Style.RESET_ALL)
        self.map = Map.Graph(self)
        self.strategy = Strategies.Strategies(self.map)

        if not mode:
            # ANARCHY
            print("BOAT SIMULATOR ANARCHY\n")
            self.cb = Controller.Boats(self, mode, num_boats)
        if mode:
            # CENTRAL CONTROL
            print("BOAT SIMULATOR CENTRAL\n")
            self.cb = Controller.Boats(self, mode, num_boats)

        self.stats.init()
        self.cb.start_now()
        demand_state = []
        for station in self.map.stations.values():
            demand_state.append(station.get_demand())
        self.stats.final_demand = demand_state
        Passenger.count = 0
        return self.stats

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
