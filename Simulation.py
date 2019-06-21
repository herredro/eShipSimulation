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
            #'dem_dist',
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



        #self.stats.print_data(central)
        #if G.visuals: self.stats.macro__plot_data(central)
        self.safe = 0
        # self.heatmap_a_b()
        # self.beta_test()
        # self.exp_num_cap()

        # self.old_school()
        #
        # self.until_wait_time(True, 20, 0)
        # self.until_wait_time(True, 20, 1)
        # #
        # self.until_wait_time(False, 20, 0)
        # self.until_wait_time(False, 20, 1)




        self.wt()
        self.sat()
        self.both()



        # self.until_wait_time(False, 100)
        #self.until_wait_time(True, 100)
    def wt(self):
        self.until_wt(True, 20, 0)
        self.until_wt(False, 20, 0)
        #
        self.until_wt(True, 20, 1)
        self.until_wt(False, 20, 1)

    def sat(self):
        self.until_satisfied(True, 90, 0)
        self.until_satisfied(False, 90, 0)
        #
        self.until_satisfied(True, 90, 1)
        self.until_satisfied(False, 90, 1)

    def both(self):
        self.until_both(True, 20, 90, 0)
        self.until_both(False, 20, 90, 0)
        #
        self.until_both(True, 20, 90, 1)
        self.until_both(False, 20, 90, 1)

    def old_school(self):
        runs=[]

        runs.append(self.combined3(True))
        runs.append(self.combined3(False))
        self.stats.macro__print_data(runs)
        #self.stats.macro__plot_num_cap(runs)
        if G.visuals: self.stats.macro__plot_data(runs)

    def until_both(self, central, goalw, goals, nohomo):
        if nohomo == 1:
            G.nohomo = 1
        if nohomo == 0:
            G.nohomo = 0
        nb = 1
        runs = []
        more_needed = True
        capacities = [10, 30, 50]
        needed = []
        print("EXPERIMENT BOTH: central=%s. to achieve wait_time=%s and sat=%s in vary=%s" % (central, goalw, goals, nohomo))
        for i in range(len(capacities)):
            while more_needed:
                run = (self.combined3(central, capacity=capacities[i], num_boats=nb, nohomo=nohomo))
                # runs.append(run)
                print("%s boats achieve wait_time: %s (%s%% satisfaction)" % (nb, run.means["P_wts"], run.satisfied))
                achieved = run.means["P_wts"]
                if run.means["P_wts"] > goalw or (run.satisfied < goals):
                    nb += 1
                    if goalw/achieved < 0.3:
                        nb=nb*2
                        continue
                    elif goalw/achieved < 0.4:
                        nb = nb + int(nb / 3)
                        continue
                    elif goalw / achieved < 0.5:
                        nb = nb + 2
                        continue

                    if goals/run.satisfied > 3:
                        nb=nb*2
                    elif goals/run.satisfied > 2:
                        nb=nb+int(nb/2)
                    elif goals / run.satisfied > 1.5:
                        nb = nb + int(nb / 3)
                    elif goals / run.satisfied > 1.1:
                        nb = nb + 2
                    continue
                else:
                    more_needed = False
                    need = run.params.num_boats
                    self.run = run
                    needed.append(need)
                    #print("FOUND SOLUTION. %s,  " % run.mode, need, " boats needed.")
                    break
            more_needed = True
            nb = 1
        print(needed)
        print("This was for, %sstations, central=%s, vary=%s" % (self.run.params.num_stations, central, nohomo))
        print()

    def until_wt(self, central, goal, nohomo):
        if nohomo == 1:
            G.nohomo = 1
        if nohomo == 0:
            G.nohomo = 0
        nb = 1
        runs = []
        more_needed = True
        capacities = [10, 30, 50]
        needed = []
        print("EXPERIMENT WT central=%s: to achieve wait_time=%s in vary=%s" % (central, goal, nohomo))
        for i in range(len(capacities)):
            while more_needed:
                run = (self.combined3(central, capacity=capacities[i], num_boats=nb, nohomo=nohomo))
                # runs.append(run)
                print("%sb's --> %s%%" % (nb, run.means["P_wts"]))
                achieved = run.means["P_wts"]
                if run.means["P_wts"] > goal:
                    nb += 1
                    if goal/achieved < 0.3:
                        nb=nb*2
                    elif goal/achieved < 0.4:
                        nb = nb + int(nb / 3)
                    elif goal / achieved < 0.5:
                        nb = nb + 2
                    continue
                else:
                    more_needed = False
                    self.run = run
                    need = run.params.num_boats
                    needed.append(need)
                    #print("FOUND SOLUTION. %s,  " % run.mode, need, " boats needed.")
                    break
            more_needed = True
            nb = 1
        print(needed)
        print("This was for, %sstations, central=%s, vary=%s" % (self.run.params.num_stations, central, nohomo))
        print()

    def until_satisfied(self, central, goal, nohomo):
        if nohomo == 1:
            G.nohomo = 1
        if nohomo == 0:
            G.nohomo = 0
        nb = 1
        runs = []
        more_needed = True
        #capacities = [10,20,30,40,50]
        capacities = [10, 30, 50]
        needed     = []
        print("EXPERIMENT SAT central=%s: to achieve dispatch of=%s%% in nohomo=%s" % (central, goal, nohomo))
        for i in range(len(capacities)):
            while more_needed:
                run = (self.combined3(central, capacity=capacities[i], num_boats=nb, nohomo=nohomo))
                #runs.append(run)
                print("%sb's --> %s sat" % (nb, run.satisfied))
                if run.satisfied < goal:
                    nb += 1
                    if goal/run.satisfied > 3:
                        nb=nb*2
                    elif goal/run.satisfied > 2:
                        nb=nb+int(nb/2)
                    elif goal / run.satisfied > 1.5:
                        nb = nb + int(nb / 3)
                    elif goal / run.satisfied > 1.1:
                        nb = nb + 2

                    continue
                else:
                    more_needed = False
                    self.run = run
                    need = run.params.num_boats
                    needed.append(need)
                    #print("FOUND SOLUTION. %s,  " % run.mode, need, " boats needed.")
                    break
            more_needed = True
            nb = 1
        print(needed)
        print("This was for, %sstations, central=%s, vary=%s" % (self.run.params.num_stations, central, nohomo))
        print()
        # print("%s, goal=%s, no-homo=%s, map=%s" % (central, goal, run.params.non_homo_dem, run.params.num_stations))
        # print("For capacities %s, needed %s" %(capacities, needed))




    def combined3(self, central, simtime=G.SIMTIME, num_stations=G.num_stations, dist_mean=G.dist_mean, dist_std=G.dist_std, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, nohomo=G.nohomo, random_seed=G.randomseed, edges=G.edgeList):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        num_st = len(edges)
        #self.dem_distr=expected_arrivals

        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, nohomo, edges, random_seed)
        #print("--CENTRAL--") if central else print("--HOHO--")
        #self.params.print()
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        self.map = Map.Graph(self, num_stations=num_stations)
        self.strategy = Strategies.Strategies(self.map)
        self.cb = Controller.Boats(self, self.central)
        self.stats.init()
        self.cb.start_now()
        self.stats.final_demand = [station.get_demand() for station in self.map.stations.values()]
        Passenger.count = 0
        self.stats.micro__analyze_data()
        return self.stats


    def num_cap(self):
        self.EXPERIMENT_NAME = "hh30"
        self.csv_out_init(self.EXPERIMENT_NAME)
        capacity = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        capacity = 30
        nb = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 2, 1]
        nb=[10]
        RUNS = len(nb)
        hoho, central = [], []
        for i in range(len(nb)):
            #hoho.append(self.combined(False, alpha=5, num_boats=nb[i], capacity=capacity))
            central.append(self.combined(False, num_boats=nb[i], capacity=capacity))

            print(i / RUNS)

    def benchmark(self):
        self.EXPERIMENT_NAME = "BenchAll"
        self.csv_out_init(self.EXPERIMENT_NAME)
        alpha, beta, cap, nb, dem = self.csv_in("csv/in/benchAll.csv")
        RUNS = len(alpha)
        hoho, central = [], []
        for i in range(RUNS):
            hoho.append(self.combined2(False, alpha=alpha[i], beta=beta[i], capacity=cap[i], num_boats=nb[i],
                                       expected_arrivals=dem[i]))
            hoho.append(self.combined2(True, alpha=alpha[i], beta=beta[i], capacity=cap[i], num_boats=nb[i],
                                       expected_arrivals=dem[i]))
            print(i / RUNS)

    def heatmap_num_cap(self):
        runs = []
        capacity = [2*i+2 for i in range(25)]
        nb = [50-2*i for i in range(25)]
        for i in range(len(nb)):
            runs.append(self.combined(True, num_boats=nb[i], capacity=capacity[i]))
        self.stats.macro__plot_num_cap(runs)

    def beta_test(self):
        runs = []
        beta = [0,1, 1.5,2, 2.5,3, 3.5,4, 4.5,5, 5.5,6, 6.5,7,8,9,10]


        for i in range(len(beta)):
            runs.append(self.combined(True, beta=beta[i]))
        for run in runs:
            print("beta=%s, satisfied: %s, waiting: %s, overdrive: %s" %(run.params.beta, run.satisfied, run.means["P_wts"], run.means["P_otb"]))

    def heatmap_a_b(self):
        runs = []
        alpha, beta = self.csv_in2("csv/in/abL.csv")

        for i in range(len(alpha)):
            runs.append(self.combined(True, alpha=alpha[i], beta=beta[i]))
        self.stats.macro__plot_ab(runs)

    def combined2(self, central, simtime=G.SIMTIME, num_stations=G.num_stations, dist_mean=G.dist_mean, dist_std=G.dist_std, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, expected_arrivals=G.expected_arrivals, random_seed=G.randomseed, edges=G.edgeList):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        num_st = len(edges)
        self.dem_distr=expected_arrivals
        if expected_arrivals == 1:
            expected_arrivals = [2,2,2,2,2,2,2,2,2]
        elif expected_arrivals == 2:
            expected_arrivals = [1,3,0,2,4,1,2,3,2]
        elif expected_arrivals == 3:
            expected_arrivals = [0,0,1,2,3,4,4,2,2]
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, expected_arrivals, edges, random_seed)
        print("--CENTRAL--") if central else print("--HOHO--")
        self.params.print()
        self.stats = Stats.Stats(self)
        self.env = simpy.Environment()
        self.map = Map.Graph(self, num_stations=num_stations)
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
        self.safe = 0

        capacity = 10
        nb = 10
        stats.append(self.combined(False, capacity=capacity, num_boats=nb, beta=2, nohomo=0))
        stats.append(self.combined(False, capacity=capacity, num_boats=nb, beta=3, nohomo=1))
        # stats.append(self.combined(True, capacity=capacity, num_boats=nb, edges=G.edgeList5))
        # stats.append(self.combined(True, capacity=capacity, num_boats=20, edges=G.edgeList5))
        # stats.append(self.combined(True, capacity=capacity, num_boats=20, edges=G.edgeList5))

        if G.visuals: self.stats.macro__plot_data(stats)

    def combined(self, central, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, random_seed=G.randomseed, edges=G.edgeList, nohomo=G.nohomo):
        self.central = central
        G.randomseed = 1
        random.seed(G.randomseed)
        self.params = Parameters(self.central, simtime, to_dock, to_pickup, to_dropoff, num_boats, capacity, alpha, beta, max_arrival, iat, nohomo, edges, random_seed)
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

    def csv_in2(self, file):
        a, b = [], []
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                a.append(int(eval(row['alpha'])))
                b.append(int(eval(row['beta'])))
        return a, b



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
