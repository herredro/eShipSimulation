import random
import logging
import numpy as np
randomseed = 12
np.random.seed(randomseed)
random.seed(randomseed)
logging.basicConfig(level=logging.ERROR, filemode="w", filename="zim.log", format="%(levelname)s - %(funcName)s - %(message)s\n")
log_pickdrop = logging.getLogger("Pick/Drop")
log_comptimes = logging.getLogger("Computation_Times")


PENALTY_ROUTE_DIVERSION = 4 # needs to be bigger than 1, otherwise reverse effect

#SIM PARAMS
SIMTIME = 1000
DOCK_TIMEOUT = 0
PICK_UP_TIMEOUT = 0
DROPOFF_TIMEOUT = 0

# RESOURCES
NUM_BOATS = 1
CAPACITY = 10
locaction=-1
startVertex = 1

# PARAMETERS ALGOS
BETA_DISCOUNT_RECURSION = 1 #best value after quick test
ALPHA_DESTINATION_MIX = 3

# DEMAND
MAX_ARRIVAL_EXPECT = 2
INTERARRIVALTIME = 10
#initial_demand = [450, 440, 420, 90, 110, 130, 150]
initial_demand   = [0,0,0,0,0,0,0,0,0,0]
expected_arrivals= [4,3,3,5,2,3,3,5,2,1]

# STATS PRINT
live = False
visuals = False
means = True
accrued_demand = True
approached_stations = True

# SIM OUTPUT
map = False
boat_creation = False







#BOAT DEFAULTS
BATTERY=100000
chargingspeed=10
consumption=1
ROUTE_LENGHT = 10


numBoats = 2
debug = 0
simpy = 1
ui_choice = 1
d_charge = 1
debug_passenger = 1
d_route_change = 1

#SIMULATION INIT VARIABLES
rounds = 2
manual = 1
semiauto = 1
highestdemand = 1 #if not, closest neighbor



#
# poisson_arrivals_expected = []
# for i in range(len(initial_demand)):
#     poisson_arrivals_expected.append(random.randint(1, MAX_ARRIVAL_EXPECT))
# poisson_arrivals = []
# for i in range(len(initial_demand)):
#     station = []
#     for i in range(len(initial_demand)):
#         for j in range(int(SIMTIME/10)):
#             station.append(np.random.poisson(poisson_arrivals_expected[i]))
#     poisson_arrivals.append(station)



d_p_num = 534


# to add edge, use: [x, y, z],
edgeList2 = [[1, 2, 10, 1],
            [1, 4,  5],
            [2, 3, 20],
            [3, 1, 50],
            [4, 2, 10],
            [1, 9,  5],
            [9, 1,  5, 1]]

edgeList9 =     [[1, 2, 10, 1],
                [2, 3, 20],
                [3, 4, 30],
                [4, 5, 40],
                [5, 6, 50],
                [6, 7, 60],
                [7, 8, 70],
                [8, 9, 80],
                [9, 1, 90]]

edgeList =     [[1, 2, 10, 1],
                [2, 3, 20],
                [3, 4, 30],
                [4, 5, 40],
                [5, 1, 50]]


edgeList2 =     [[1, 2, 10, 1],
                [2, 3, 20],
                [3, 1, 60]]

edgeList3 =     [[1, 2, 10, 1],
                 [3, 4, 30],
                 [2, 3, 20],
                 [3, 2, 20],
                 [4, 3, 30],
                 [4, 1, 40],
                 [1, 4, 40]]

edgeListFork = [[1, 2, 10, 1],
            [1, 3, 50],
            [2, 4, 20],
            [4, 1, 10],
            [3, 4, 10]]
