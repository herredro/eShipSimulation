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
        self.fieldnames = [
            'simtime',
            'rand',
            'meth',
            'alpha',
            'beta',
            'num_boats',
            'capacity',
            'mn_boatload_ratio',
            'num_stations',
            'avgdist',
            'stddist',
            'avgexpdem',
            'stdexpdem',
            'dispatched',
            'dropped',
            'waiting',
            'dem_occ',
            'dem_left',
            'mn_waiting_demand',
            'p_wts',
            'p_otb',
            'satisfied']

        self.safe = "benchmarkALL"
        self.benchmark()
        # self.combined(True, num_boats=50, capacity=10, alpha=4)
        # self.exp_num_a()
        # self.test2()
        #self.one()
        # self.safe="alpha_on_cap10num50"
        # if self.safe != 0: self.csv_out_init(self.safe)
        # self.combined(True, num_boats=10, capacity=50, alpha=1)
        # self.combined(True, num_boats=10, capacity=50, alpha=2)
        # self.combined(True, num_boats=10, capacity=50, alpha=3)
        # self.combined(True, num_boats=10, capacity=50, alpha=4)
        # self.combined(True, num_boats=10, capacity=50, alpha=5)
        # self.combined(True, num_boats=10, capacity=50, alpha=6)
        # self.combined(True, num_boats=10, capacity=50, alpha=7)
        # self.exp_cap100()
        #self.exp_cap10()
        #self.exp_cap30()
        #self.old_school()
        #self.freestyle()

        #self.stats.print_data(central)
        #if G.visuals: self.stats.macro__plot_data(central)

    def combined2(self, central, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, expected_arrivals=G.expected_arrivals, random_seed=G.randomseed, edges=G.edgeList):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        num_st = len(edges)
        if expected_arrivals == 1:
            expected_arrivals = [2,2,2,2,2,2,2,2]
        elif expected_arrivals == 2:
            expected_arrivals = [1,3,0,2,4,1,2,3]
        elif expected_arrivals == 3:
            expected_arrivals = [0, 0, 1, 2, 3, 4, 4, 2]
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, expected_arrivals, edges, random_seed)
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
        if self.safe != 0: self.csv_out(self.stats.csv_output(), self.safe)
        return self.stats


    def freestyle(self):
        stats = []
        self.safe = "Freestyle"

        capacity = 10
        nb = 10
        stats.append(self.combined(False, capacity=capacity, num_boats=nb))
        stats.append(self.combined(True, capacity=capacity, num_boats=nb))
        stats.append(self.combined(False, capacity=capacity, num_boats=nb, edges=G.edgeList5))
        stats.append(self.combined(True, capacity=capacity, num_boats=nb, edges=G.edgeList5))
        stats.append(self.combined(False, capacity=capacity, num_boats=20, edges=G.edgeList5))
        stats.append(self.combined(True, capacity=capacity, num_boats=20, edges=G.edgeList5))

        if G.visuals: self.stats.macro__plot_data(stats)

    def combined(self, central, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, expected_arrivals=G.expected_arrivals, random_seed=G.randomseed, edges=G.edgeList):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, expected_arrivals, edges, random_seed)
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
        if self.safe != 0: self.csv_out(self.stats.csv_output(), self.safe)
        return self.stats


    def csv_out_init(self, name):
        with open('csv/out/%s.csv'%name, mode='w') as csv_file:

            csv_file.write("sep=,\n")
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()

    def csv_out(self, stats, name):
        with open('csv/out/%s.csv'%self.safe, mode='a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writerow(stats)

    def old_school(self):
        runs=[]

        runs.append(self.combined(False))
        runs.append(self.combined(True))
        self.stats.macro__print_data(runs)
        self.stats.macro__plot_num_cap(runs)
        if G.visuals: self.stats.macro__plot_data(runs)

    def benchmark(self):
        self.EXPERIMENT_NAME = "BenchAll"
        self.csv_out_init(self.EXPERIMENT_NAME)
        alpha, beta, cap, nb, dem = self.csv_in("csv/in/benchall.csv")
        RUNS = len(alpha)
        hoho, central = [], []
        for i in range(4):
            hoho.append(self.combined2(False, alpha=alpha[i], beta=beta[i], capacity=cap[i], num_boats=nb[i], expected_arrivals=dem))
            hoho.append(self.combined2(True, alpha=alpha[i], beta=beta[i], capacity=cap[i], num_boats=nb[i], expected_arrivals=dem))
            print(i / RUNS)

    def one(self):
        a = [self.combined(True, capacity=200, num_boats=1)]
        self.stats.macro__plot_data(a)



    def test(self):
        ## FINDINGS: the smaller capacity, the better central.

        capacity=10
        self.combined(False, capacity=capacity, num_boats=2)
        self.combined(True, capacity= capacity, num_boats=2)
        self.combined(False, capacity=capacity, num_boats=4)
        self.combined(True, capacity= capacity, num_boats=4)
        self.combined(False, capacity=capacity, num_boats=6)
        self.combined(True, capacity= capacity, num_boats=6)
        self.combined(False, capacity=capacity, num_boats=8)
        self.combined(True, capacity= capacity, num_boats=8)
        print("##################################################")
        print("##################################################")
        capacity = 30
        self.combined(False, capacity=capacity, num_boats=2)
        self.combined(True, capacity=capacity, num_boats=2)
        self.combined(False, capacity=capacity, num_boats=4)
        self.combined(True, capacity=capacity, num_boats=4)
        self.combined(False, capacity=capacity, num_boats=6)
        self.combined(True, capacity=capacity, num_boats=6)
        self.combined(False, capacity=capacity, num_boats=8)
        self.combined(True, capacity=capacity, num_boats=8)
        print("##################################################")
        print("##################################################")
        capacity = 60
        self.combined(False, capacity=capacity, num_boats=2)
        self.combined(True, capacity=capacity, num_boats=2)
        self.combined(False, capacity=capacity, num_boats=4)
        self.combined(True, capacity=capacity, num_boats=4)
        self.combined(False, capacity=capacity, num_boats=6)
        self.combined(True, capacity=capacity, num_boats=6)
        self.combined(False, capacity=capacity, num_boats=8)
        self.combined(True, capacity=capacity, num_boats=8)

    def exp_cap10(self):
        self.EXPERIMENT_NAME = "cap10"
        self.csv_out_init(self.EXPERIMENT_NAME)
        capacity = 10
        nb = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        RUNS = len(nb)
        hoho, central = [], []
        for i in range(RUNS):
            hoho.append(self.combined(False, num_boats=nb[i], capacity=capacity))
            central.append(self.combined(True, num_boats=nb[i], capacity=capacity))
            print(i / RUNS)

    def exp_cap30(self):
        self.EXPERIMENT_NAME = "cap30"
        self.csv_out_init(self.EXPERIMENT_NAME)
        capacity = 30
        nb = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        RUNS = len(nb)
        hoho, central = [], []
        for i in range(RUNS):
            hoho.append(self.combined(False, num_boats=nb[i], capacity=capacity))
            central.append(self.combined(True, num_boats=nb[i], capacity=capacity))
            print(i / RUNS)

    def exp_cap100(self):
        self.EXPERIMENT_NAME = "cap100"
        self.csv_out_init(self.EXPERIMENT_NAME)
        capacity = 100
        nb = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        RUNS = len(nb)
        hoho, central = [], []
        for i in range(RUNS):
            hoho.append(self.combined(False, num_boats=nb[i], capacity=capacity))
            central.append(self.combined(True, num_boats=nb[i], capacity=capacity))
            print(i / RUNS)



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

    def csv_in(self, file):
        first, second = [], []
        a,b,c,d,e = [], [], [], [], []
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                a.append(int(eval(row['alpha'])))
                b.append(int(eval(row['beta'])))
                c.append(int(eval(row['cap'])))
                d.append(int(eval(row['nb'])))
                e.append(int(eval(row['dem'])))
        return a, b, c, d, e



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
