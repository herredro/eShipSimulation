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





class Simulation:
    def __init__(self):
        hoho = []
        central = []
        num_boats = [1, 1, 1, 1, 1]
        capacity = [10, 10, 10, 10, 10]
        alpha = [i + 2 for i in range(6)] * 5
        beta = [i + 1 for i in range(6)] * 5
        max_arrival = []
        for i in range(10):
            #hoho.append(self.combined(False, alpha=alpha[i]))
            central.append(self.combined(True, alpha=alpha[i], beta=beta[i]))
            # same arising demand?


        # data.append(self.simpy(False))
        random.seed(G.randomseed)
        # data.append(self.simpy(True))

        #self.stats.print_data(central)
        if G.visuals: self.stats.macro__plot_data(central)

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
