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
SIMTIME = 720 #12h operation
DOCK_TIMEOUT = 2
PICK_UP_TIMEOUT = 0
DROPOFF_TIMEOUT = 0

#MAP PARAMS
num_stations=20
dist_mean=10
dist_std=5

# RESOURCES
NUM_BOATS = 90
CAPACITY = 10
locaction=-1
startVertex = 1

# PARAMETERS ALGOS
BETA_DISCOUNT_RECURSION = 3 #best value after quick test
ALPHA_DESTINATION_MIX = 5

# DEMAND
MAX_ARRIVAL_EXPECT = 2
INTERARRIVALTIME = 20
#initial_demand = [450, 440, 420, 90, 110, 130, 150]
initial_demand   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# expected_arrivals= [1,3,4,3,2,3,1,1,2,3,1,1,2,1,1,2]
# expected_arrivals= [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
# expected_arrivals= [1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3]
# expected_arrivals= [1,2,3,4,15,2,3,4,1,2,3,4,2,2,2,2,2]
nohomo = 0
exp_arr = 5
# UNIFORM
expected_arrivals = [exp_arr]*num_stations

# VARYING
expected_arrivals2 = [exp_arr]*num_stations

expected_arrivals1= expected_arrivals2.copy()
expected_arrivals1[1]*=4
expected_arrivals1[2]*=4
expected_arrivals1[3]*=4

expected_arrivals3= expected_arrivals.copy()
expected_arrivals3[-5]*=4
expected_arrivals3[-4]*=4
expected_arrivals3[-3]*=4
a=1
# expected_arrivals= [i%4+1 for i in range(25)]
# expected_arrivals= [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]

# STATS PRINT
live = False
visuals = True
means = True
accrued_demand = True
approached_stations = False

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

# to add edge, use: [x, y, z],
edgeList2 = [[1, 2, 10, 1],
            [1, 4,  5],
            [2, 3, 20],
            [3, 1, 50],
            [4, 2, 10],
            [1, 9,  5],
            [9, 1,  5, 1]]

edgeList15 =     [[1, 2,  15, 1],
                [2, 3,  15],
                [3, 4,  15],
                [4, 5,  15],
                [5, 6,  15],
                [6, 7,  15],
                [7, 8,  15],
                [8, 9,  15],
                [9, 10, 15],
                [10, 11,15],
                [11, 12,15],
                [12, 13,15],
                [13, 14,15],
                [14, 15,15],
                [15, 1, 15]]

edgeList25 =   [[1, 2,   5, 1],
                [2,  3,  5],
                [3,  4,  5],
                [4,  5,  5],
                [5,  6,  5],
                [6,  7,  5],
                [7,  8,  5],
                [8,  9,  5],
                [9,  10, 5],
                [10, 11, 5],
                [11, 12, 5],
                [12, 13, 5],
                [13, 14, 5],
                [14, 15, 5],
                [15, 16, 5],
                [16, 17, 5],
                [17, 18, 5],
                [18, 19, 5],
                [19, 20, 5],
                [20, 21, 5],
                [21, 22, 5],
                [22, 23, 5],
                [23, 24, 5],
                [24, 25, 5],
                [25,  1, 5]]

edgeListC =     [[1, 2, 10, 1],
                [2, 3, 20],
                [3, 4, 20],
                [4, 5, 20],
                [5, 1, 20]]

edgeList =     [[1, 2, 10],
                [2, 3, 20],
                [3, 4, 20],
                [4, 5, 20],
                [5, 1, 20]]

edgeList8 =     [[1, 2, 15, 1],
                [2, 3, 15],
                [3, 4, 15],
                [4, 5, 15],
                [5, 6, 15],
                [6, 7, 15],
                [7, 8, 15],
                [8, 1, 15]]

# edgeList =     [[1, 2, 5, 1],
#                 [2, 3, 5],
#                 [3, 4, 5],
#                 [4, 5, 5],
#                 [5, 6, 5],
#                 [6, 7, 5],
#                 [7, 8, 5],
#                 [8, 1, 5]]

edgeList4 =     [[1, 2, 15, 1],
                [2, 3, 15],
                [3, 4, 15],
                [4, 1, 15]]


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
