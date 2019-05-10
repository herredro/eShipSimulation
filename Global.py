import logging
logging.basicConfig(level=logging.INFO, filemode="w", filename="zim.log", format="%(levelname)s - %(funcName)s - %(message)s\n")
log_pickdrop = logging.getLogger("Pick/Drop")


debug = 0
simpy = 1
ui_choice = 1

#SIMULATION INIT VARIABLES
startVertex = 1
numBoats = 2
rounds = 2

manual = 1
semiauto = 1

highestdemand = 1 #if not, closest neighbor



initial_demand = [20, 30, 40, 50, 60, 70, 80]



# to add edge, use: [x, y, z],
edgeList2 = [[1, 2, 10, 1],
            [1, 4,  5],
            [2, 3, 20],
            [3, 1, 50],
            [4, 2, 10],
            [1, 9,  5],
            [9, 1,  5, 1]]

edgeList =[[1, 2, 5, 1],
                [2, 3, 15],
                [3, 1, 10]]

edgeListFork = [[1, 2, 10, 1],
            [1, 3, 50],
            [2, 4, 20],
            [4, 1, 10],
            [3, 4, 10]]
