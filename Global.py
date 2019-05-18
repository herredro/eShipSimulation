import logging
logging.basicConfig(level=logging.INFO, filemode="w", filename="zim.log", format="%(levelname)s - %(funcName)s - %(message)s\n")
log_pickdrop = logging.getLogger("Pick/Drop")

#BOAT DEFAULTS
locaction=-1
battery=100
chargingspeed=10
consumption=1

SIMTIME = 1000

MAX_ARRIVAL_EXPECT = 5
INTERARRIVALTIME = 10


debug = 1
simpy = 1
ui_choice = 1

d_charge = 1
debug_passenger = 1

#SIMULATION INIT VARIABLES
startVertex = 1
numBoats = 2
rounds = 2

manual = 1
semiauto = 1

highestdemand = 1 #if not, closest neighbor



initial_demand = [5, 5, 5, 90, 110, 130, 150]



# to add edge, use: [x, y, z],
edgeList2 = [[1, 2, 10, 1],
            [1, 4,  5],
            [2, 3, 20],
            [3, 1, 50],
            [4, 2, 10],
            [1, 9,  5],
            [9, 1,  5, 1]]

edgeList =     [[1, 2, 10, 1],
                [2, 3, 15],
                [3, 1, 20, 1]]

edgeListFork = [[1, 2, 10, 1],
            [1, 3, 50],
            [2, 4, 20],
            [4, 1, 10],
            [3, 4, 10]]
